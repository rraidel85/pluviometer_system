import Diary_Precipitation_Concentration_Index
import pandas as pd

def select_pluviometer():
    """Page to select the pluviometer for ci_index calculation"""
    pluvs = db(db.Pluviometer.id > 0).select(db.Pluviometer.id, db.Pluviometer.name)
    return locals()

def select_pluviometer_by_month():
    """Page to select the pluviometer for ci_index by month calculation"""
    pluvs = db(db.Pluviometer.id > 0).select(db.Pluviometer.id, db.Pluviometer.name)
    return locals()

def select_area():
    """Page to select the area for ci_index calculation"""
    # For now just show the areas who has registers in PrecipitationConcentrationIndex_By_Area table
    c_index_areas = db(db.PrecipitationConcentrationIndex_By_Area.id > 0).select(db.PrecipitationConcentrationIndex_By_Area.id_area)
    return locals()

def select_area_by_month():
    """Page to select the area for ci_index by month calculation"""
    # For now just show the areas who has registers in PrecipitationConcentrationIndex_By_Area table
    c_index_areas = db(db.PrecipitationConcentrationIndex_By_Area.id > 0).select(db.PrecipitationConcentrationIndex_By_Area.id_area)
    return locals()

def to_show_ci_for_selected_pluviometer():
    """
    Este es el que debes invocar desde la vista del mapa
    Returns:
    """
    id_pluviom = request.vars.pluv_select if request.vars.pluv_select else request.args(0, cast=int)
    pluv_name = db.Pluviometer(id_pluviom).name
    already_calculated = db(
        db.PrecipitationConcentrationIndex_By_Pluviometer.id_pluviometer == id_pluviom).select().first()
    if already_calculated is None:
        calculate_ci_generic(id_pluviom)
    pluvs = db(db.PrecipitationConcentrationIndex_By_Pluviometer.id_pluviometer == id_pluviom).select()

    # halar también los registros de los meses, por id_pluviometer igualito
    return dict(pluvs=pluvs,pluv_name=pluv_name)

def to_show_ci_for_selected_pluviometer_by_month():
    id_pluviom = request.vars.pluv_select if request.vars.pluv_select else request.args(0, cast=int)
    pluv_name = db.Pluviometer(id_pluviom).name
    pluvs = db(db.PrecipitationConcentrationIndex_Monthly_By_Pluviometer.id_pluviometer == id_pluviom).select()

    return dict(pluvs=pluvs,pluv_name=pluv_name)

def to_show_ci_for_selected_area():
    """
    Este es el que debes invocar desde la vista del mapa
    Returns:

    """
    id_area = request.vars.area_select if request.vars.area_select else request.args(0, cast=int)
    area_name = db.Area(id_area).name
    already_calculated = db(
        db.PrecipitationConcentrationIndex_By_Area.id_area == id_area).select().first()
    if already_calculated is None:
        calculate_ci_generic(id_area, is_area=True)
    areas = db(db.PrecipitationConcentrationIndex_By_Area.id_area == id_area).select()
    # halar también los registros de los meses, por id_pluviometer igualito
    return dict(areas=areas,area_name=area_name)


def to_show_ci_for_selected_area_by_month():
    id_area = request.vars.area_select if request.vars.area_select else request.args(0, cast=int)
    area_name = db.Area(id_area).name
    areas = db(db.PrecipitationConcentrationIndex_Monthly_By_Area.id_area == id_area).select()

    return dict(areas=areas,area_name=area_name)

################################################
# Helper functions
################################################
def calculate_ci_generic(id_element, is_area=None):
    if is_area:
        rows_registers = db(db.Pluviometer_Area.id_area == id_element).select(db.Pluviometer_Area.id_pluviometer)
        pluvs_ids = [row.id_pluviometer for row in rows_registers]
    else:
        pluvs_ids = [id_element]

    pluvs_condition_query_Registers = None
    pluvs_condition_query_YearStatistics = None
    for pluv in pluvs_ids:
        if not pluvs_condition_query_Registers:
            pluvs_condition_query_Registers = db.Registers.id_pluviometer == pluv
            pluvs_condition_query_YearStatistics = db.YearStatistics.id_pluviometer == pluv
        else:
            pluvs_condition_query_Registers |= db.Registers.id_pluviometer == pluv
            pluvs_condition_query_YearStatistics |= db.YearStatistics.id_pluviometer == pluv

    stats = {}

    years_considered = db(pluvs_condition_query_YearStatistics & (db.YearStatistics.total_precipit > 0)).count()
    years_not_to_consider = db(pluvs_condition_query_YearStatistics & (db.YearStatistics.total_precipit == 0)).count()

    resume_df = pd.DataFrame()
    total_registers = []
    total_non_rainy_days = 0
    for month in db().select(db.MonthNomenclator.id):
        second_query = (db.Registers.register_date.month() == month.id) & (db.Registers.rain_value > 0)
        count_query = (db.Registers.register_date.month() == month.id) & (db.Registers.rain_value == 0)

        # Query for all registers for a given month and an area of pluviometers
        full_registers_query = pluvs_condition_query_Registers & second_query
        rows_registers = db(full_registers_query).select(db.Registers.rain_value)
        registers = [row.rain_value for row in rows_registers]

        non_rainy_days = db(count_query & pluvs_condition_query_Registers).count() - 30 * years_not_to_consider
        total_non_rainy_days += non_rainy_days

        total_registers.extend(registers)
        monthly_data = calculate_statistics(registers, years_considered, non_rainy_days, month.id)
        resume_df = resume_df.append(monthly_data)
        if is_area:
            persist_area_data(monthly_data, id_element, years_considered, month.id)
        else:
            persist_pluviometer_data(monthly_data, id_element, years_considered, month.id)

    global_data = calculate_statistics(total_registers, years_considered, total_non_rainy_days)
    if is_area:
        persist_area_data(global_data, id_element, years_considered)
    else:
        persist_pluviometer_data(global_data, id_element, years_considered)

    return dict(resume_df=resume_df, columns=resume_df.columns)


def calculate_statistics(registers, years_considered, non_rainy_days, month=None):
    ci_calculator = Diary_Precipitation_Concentration_Index.Diary_Precipitation_Concentration_Index(
        registers, '')
    rainy_days = ci_calculator.df['cumulative_freq_stacked_sum_ni'].iat[-1]
    resume_df = pd.DataFrame([[
        ci_calculator.pars_exp[0],  # a
        ci_calculator.pars_exp[1],  # b
        round(ci_calculator.R_2, 4),  # R^2
        round(ci_calculator.ci, 3),  # Coef concentración de precipitaciones
        round(rainy_days, 2),  # Días con lluvia (Total)
        round(ci_calculator.sum_registered_values, 2),  # mm de lluvia (total)
        round(ci_calculator.max_registered_value, 2),  # Máxima precipitación registrada
        round(ci_calculator.sum_registered_values / years_considered, 2),  # mm de lluvia x mes (promedio)
        round(rainy_days / years_considered, 2),  # Días lluviosos x mes (promedio)
        round((rainy_days / (rainy_days + non_rainy_days)) * 100, 2),  # Porciento de días lluviosos
    ]],
        columns=['a_value',
                 'b_value',
                 'r_2_value',
                 'ci_value',
                 'rainy_days',
                 'total_rain_value',
                 'max_rain_value',
                 'rain_by_period_avg',
                 'rainy_days_by_period_avg',
                 'rainy_days_percent',
                 ],
        index=[('mes ' + str(month) if month else 'valores para el área')])
    return resume_df


def persist_area_data(df_data, id_area, years_considered, month_id=None):
    dict_to_insert = {'id_area': id_area,
                      'years_considered': years_considered}
    for column in df_data.columns:
        dict_to_insert[column] = df_data[column].iat[0]
    if month_id:
        dict_to_insert['month_value'] = month_id
        db.PrecipitationConcentrationIndex_Monthly_By_Area.insert(**dict_to_insert)
    else:
        db.PrecipitationConcentrationIndex_By_Area.insert(**dict_to_insert)


def persist_pluviometer_data(df_data, id_pluviometer, years_considered, month_id=None):
    dict_to_insert = {'id_pluviometer': id_pluviometer,
                      'years_considered': years_considered}
    for column in df_data.columns:
        dict_to_insert[column] = df_data[column].iat[0]
    if month_id:
        dict_to_insert['month_value'] = month_id
        db.PrecipitationConcentrationIndex_Monthly_By_Pluviometer.insert(**dict_to_insert)
    else:
        db.PrecipitationConcentrationIndex_By_Pluviometer.insert(**dict_to_insert)
