AreaType_format = '%(name)s'
db.define_table("AreaType",
                Field("name", "string", default=None, label='Nombre'),
                Field("representation", "string", default=None, label='Representación'),
                Field("description", "text", default=None, label='Descripción'),
                format=AreaType_format)

db.AreaType.name.requires = [IS_NOT_EMPTY(error_message='Este campo es obligatorio')]
db.AreaType.representation.requires = [IS_NOT_EMPTY(error_message='Este campo es obligatorio')]

PluviometerType_format = '%(name)s'
db.define_table("PluviometerType",
                Field("name", "string", default=None, label='Tipo de pluviómetro'),
                Field("description", "text", default=None, label='Descripción'),
                format=PluviometerType_format)

db.PluviometerType.name.requires = [IS_NOT_EMPTY(error_message='Este campo es obligatorio')]

Pluviometer_format = '%(name)s'
db.define_table("Pluviometer",
                Field("id_pluviometer_type", db.PluviometerType, label='Tipo'),
                Field("name", "string", notnull=True, default='NULL', label='Identificador'),
                Field("station_name", "string", label='Nombre de la estación'),
                Field("msnm", "integer", label='Altura sobre el nivel del mar'),
                Field("lat", "double", default=None, label='Latitud'),
                Field("lon", "double", default=None, label='Longitud'),
                format=Pluviometer_format)
db.Pluviometer._singular = T('Pluviómetro')
db.Pluviometer._plural = T('Pluviómetros')
db.Pluviometer.id.readable = False

db.Pluviometer.name.requires = [IS_NOT_EMPTY(error_message='Este campo es obligatorio')]

db.define_table("Registers",
                Field("id_pluviometer", db.Pluviometer, label='Pluviómetro'),
                Field("register_date", "date", notnull=True, default='NULL', label='Fecha'),
                Field("rain_value", "double", default=None, label='Valor de precipitación registrado'))
db.Registers._singular = T('Registro')
db.Registers._plural = T('Registros')
db.Registers.id.readable = False

db.Registers.register_date.requires = [IS_NOT_EMPTY(error_message='Este campo es obligatorio')]
db.Registers.rain_value.requires = [IS_NOT_EMPTY(error_message='Este campo es obligatorio')]

YearStatistics_format = '%(year_number)s'
db.define_table("YearStatistics",
                Field("id_pluviometer", db.Pluviometer, label="Pluviómetro"),
                Field("year_number", "integer", label='Año'),
                Field("total_precipit", "double", default=None, label='Precipitaciones totales'),
                Field("max_registered_value", "double", default=None, label='Valor máximo registrado'),
                Field("daily_mean", "double", default=None, label='Media diaria'),
                Field("rainy_days_count", "integer", default=None, label='Días lluviosos'),
                Field("rainy_streak_count", "integer", default=None, label='Rachas lluviosas'),
                Field("rainy_streak_med_long", "double", default=None, label='Longitud media de las rachas lluviosas'),
                format=YearStatistics_format)
db.YearStatistics._singular = T('Estadística anual')
db.YearStatistics._plural = T('Estadísticas anuales')
db.YearStatistics.id.readable = False


MonthNomenclator_format = '%(month_number)s'
db.define_table("MonthNomenclator",
                Field("month_name", "string", notnull=True, label='Mes'),
                format=MonthNomenclator_format)
db.MonthNomenclator._singular = T('mes')
db.MonthNomenclator._plural = T('meses')
db.MonthNomenclator.id.readable = False


MonthStatistics_format = '%(month_number)s'
db.define_table("MonthStatistics",
                Field("id_year", db.YearStatistics, label='Año'),
                Field("month_number", db.MonthNomenclator, notnull=True, label='Mes'),
                Field("total_precipit", "double", default=0, label='Precipitaciones totales'),
                Field("max_registered_value", "double", default=0, label='Valor máximo registrado'),
                Field("daily_mean", "double", default=None, label='Media diaria'),
                Field("rainy_days_count", "integer", default=0, label='Días lluviosos'),
                Field("standard_deviation", "double", default=0, label='Desviación estándar'),
                Field("variance", "double", default=None, label='Varianza'),
                Field("rainy_streak_count", "integer", default=None, label='Rachas lluviosas'),
                Field("rainy_streak_med_long", "double", default=None, label='Longitud media de las rachas lluviosas'),
                format=MonthStatistics_format)
db.MonthStatistics._singular = T('Estadística mensual')
db.MonthStatistics._plural = T('Estadísticas mensuales')
db.MonthStatistics.id.readable = False

Area_format = '%(name)s'
db.define_table("Area",
                Field("id_area_type", db.AreaType, label='Tipo de área'),
                Field("name", "string", default=None, label='Nombre'),
                Field("sub_name", "string", default=None, label='Nombre Específico'),
                Field("description", "text", default=None, label='Descripción'),
                Field("centroid_lat", "double", default=None, label='Latitud del centroide'),
                Field("centroid_lon", "double", default=None, label='Longitud del centroide'),
                format=Area_format)

db.Area.name.requires = [IS_NOT_EMPTY(error_message='Este campo es obligatorio')]

db.define_table("AreaNode",
                Field("id_area", db.Area, label='Área'),
                Field("lat", "double", default=None, label='Latitud'),
                Field("lon", "double", default=None, label='Longitud'),
                Field("step", "integer"))

db.define_table("Pluviometer_Area",
                Field("id_area", db.Area, label='Área'),
                Field("id_pluviometer", db.Pluviometer, label='Pluviómetro'))

db.define_table("PrecipitationConcentrationIndex_By_Area",
                Field("id_area", db.Area, label='Área'),
                Field("years_considered", 'integer', label='Años considerados'),
                Field("a_value", 'double', label='Valor de "a"'),
                Field("b_value", 'double', label='Valor de "b"'),
                Field("r_2_value", 'double', label='R^2'),
                Field("ci_value", 'double', label='Índice de concentración'),
                Field("rainy_days", 'integer', label='Días con lluvia (total)'),
                Field("total_rain_value", 'double', label='Total de precipitaciones registradas'),
                Field("max_rain_value", 'double', label='Máxima precipitación registrada'),
                Field("rain_by_period_avg", 'double', label='mm de lluvia (promedio anual)'),
                Field("rainy_days_by_period_avg", 'double', label='Días lluviosos (promedio anual)'),
                Field("rainy_days_percent", 'double', label='Porciento de días lluviosos al año'),
                )

db.define_table("PrecipitationConcentrationIndex_Monthly_By_Area",
                Field("id_area", db.Area, label='Área'),
                Field("years_considered", 'integer', label='Años considerados'),
                Field("month_value", db.MonthNomenclator, label='Mes'),
                Field("a_value", 'double', label='Valor de "a"'),
                Field("b_value", 'double', label='Valor de "b"'),
                Field("r_2_value", 'double', label='R^2'),
                Field("ci_value", 'double', label='Índice de concentración'),
                Field("rainy_days", 'integer', label='Días con lluvia (total)'),
                Field("total_rain_value", 'double', label='Total de precipitaciones registradas'),
                Field("max_rain_value", 'double', label='Máxima precipitación registrada'),
                Field("rain_by_period_avg", 'double', label='mm de lluvia (promedio)'),
                Field("rainy_days_by_period_avg", 'double', label='Días lluviosos (promedio)'),
                Field("rainy_days_percent", 'double', label='Porciento de días lluviosos'),
                )

db.define_table("PrecipitationConcentrationIndex_By_Pluviometer",
                Field("id_pluviometer", db.Pluviometer, label='Pluviómetro'),
                Field("years_considered", 'integer', label='Años considerados'),
                Field("a_value", 'double', label='Valor de "a"'),
                Field("b_value", 'double', label='Valor de "b"'),
                Field("r_2_value", 'double', label='R^2'),
                Field("ci_value", 'double', label='Índice de concentración'),
                Field("rainy_days", 'integer', label='Días con lluvia (total)'),
                Field("total_rain_value", 'double', label='Total de precipitaciones registradas'),
                Field("max_rain_value", 'double', label='Máxima precipitación registrada'),
                Field("rain_by_period_avg", 'double', label='mm de lluvia (promedio anual)'),
                Field("rainy_days_by_period_avg", 'double', label='Días lluviosos (promedio anual)'),
                Field("rainy_days_percent", 'double', label='Porciento de días lluviosos al año'),
                )
db.define_table("PrecipitationConcentrationIndex_Monthly_By_Pluviometer",
                Field("id_pluviometer", db.Pluviometer, label='Pluviómetro'),
                Field("years_considered", 'integer', label='Años considerados'),
                Field("month_value", db.MonthNomenclator, label='Mes'),
                Field("a_value", 'double', label='Valor de "a"'),
                Field("b_value", 'double', label='Valor de "b"'),
                Field("r_2_value", 'double', label='R^2'),
                Field("ci_value", 'double', label='Índice de concentración'),
                Field("rainy_days", 'integer', label='Días con lluvia (total)'),
                Field("total_rain_value", 'double', label='Total de precipitaciones registradas'),
                Field("max_rain_value", 'double', label='Máxima precipitación registrada'),
                Field("rain_by_period_avg", 'double', label='mm de lluvia (promedio)'),
                Field("rainy_days_by_period_avg", 'double', label='Días lluviosos (promedio)'),
                Field("rainy_days_percent", 'double', label='Porciento de días lluviosos'),
                )

""" Relations between tables (remove fields you don't need from requires) """
db.Registers.id_pluviometer.requires = IS_IN_DB(db, 'Pluviometer.id',
                                                ' %(name)s ', zero=None)
db.Pluviometer.id_pluviometer_type.requires = IS_IN_DB(db, 'PluviometerType.id', ' %(name)s ')
db.MonthStatistics.id_year.requires = IS_IN_DB(db, 'YearStatistics.id',
                                               ' %(year_number)s ', zero=None)
db.YearStatistics.id_pluviometer.requires = IS_IN_DB(db, 'Pluviometer.id',
                                                     ' %(name)s ', zero=None)
db.Area.id_area_type.requires = IS_IN_DB(db, 'AreaType.id', ' %(name)s ', zero=None)
db.AreaNode.id_area.requires = IS_IN_DB(db, 'Area.id',
                                        ' %(name)s ', zero=None)
db.Pluviometer_Area.id_area.requires = IS_IN_DB(db, 'Area.id',
                                                ' %(name)s ', zero=None)
db.Pluviometer_Area.id_pluviometer.requires = IS_IN_DB(db, 'Pluviometer.id',
                                                       ' %(name)s ', zero=None)




# COMENZANDO A CARGAR INFORMACIÓN A LA BASE DE DATOS

# exist_pluviometer_data = db().select(db.Pluviometer.name).first()
# if not exist_pluviometer_data:
#     print('no hay datos, comenzando la importación')

#     import pandas as pd
#     import Historic_Data_Processor as hdp
#     from datetime import date

#     historic_data = hdp.Historic_Data_Processor('applications/Rainy_Statsistics/modules/historic_data.pkl')

#     pluviometers = historic_data.get_pluviometers_names()
#     new_pluviometerType_id = db.PluviometerType.insert(name='Tipo por defecto',
#                                                        description='Ninguna por ahora')

#     for pluv in pluviometers:
#         new_pluviometer_id = db.Pluviometer.insert(name=pluv,
#                                                    id_pluviometer_type=new_pluviometerType_id)

#         years_registered = historic_data.get_years_registered(pluv)
#         for year in years_registered:
#             month_full_reg, year_statistics = historic_data.get_year_statistics(pluv, year)
#             dict_to_save_year_stats = {}
#             for reg in year_statistics.index:
#                 try:
#                     if not pd.isnull(year_statistics[reg]):
#                         dict_to_save_year_stats[reg] = year_statistics[reg]
#                 except:
#                     continue

#             dict_to_save_year_stats['id_pluviometer'] = new_pluviometer_id
#             dict_to_save_year_stats['year_number'] = year
#             print('pluviometro {0}, año {1}'.format(pluv, year))
#             new_registerd_year_id = db.YearStatistics.insert(**dict_to_save_year_stats)

#             month_stats = month_full_reg.iloc[:, 31:]
#             for month in month_stats.index:
#                 dict_to_save_month_stats = {'month_number': month}
#                 for reg in month_stats.columns:
#                     # print('mes {0}, variable {1}'.format(month, reg))
#                     try:
#                         if not pd.isnull(month_stats.at[month, reg]):
#                             dict_to_save_month_stats[reg] = month_stats.at[month, reg]
#                     except:
#                         continue

#                 dict_to_save_month_stats['id_year'] = new_registerd_year_id
#                 db.MonthStatistics.insert(**dict_to_save_month_stats)

#             month_days_reg = month_full_reg.iloc[:, :31]
#             for month in month_days_reg.index:
#                 for day in month_days_reg.columns:
#                     if not pd.isnull(month_days_reg.at[month, day]):
#                         dict_to_save_daily_reg = {}
#                         day_number = day[3:]
#                         dict_to_save_daily_reg['register_date'] = date(year=int(year), month=int(month), day=int(day_number))
#                         # dict_to_save_daily_reg['register_date']='{0}-{1}-{2}'.format(year,month,day_number)
#                         dict_to_save_daily_reg['rain_value'] = month_days_reg.at[month, day]
#                         dict_to_save_daily_reg['id_pluviometer'] = new_pluviometer_id
#                         db.Registers.insert(**dict_to_save_daily_reg)
#     print('terminé la importación de los datos')
# else:
#     print('Ya tengo información')

# CARGA DE INFORMACIÓN A LA BASE DE DATOS CONCLUIDA

#
# exist_munic_data = db(db.Area.id_area_type == 2).select().first()
# if not exist_munic_data:
#     print('no hay datos, comenzando la importación')
#     import pandas as pd
#
#     xlsx = pd.ExcelFile('applications/Rainy_Statsistics/models/Vertices_municipios_Ciego.xlsx')
#     df = pd.read_excel(xlsx)
#
#     id_area = 0
#
#     munic_actual = ''
#     sub_area = 0
#     for dot in df.index:
#         dict_to_add = {}
#         if df['vertex_part_index'][dot] == 0:
#             if df['MUNICIPIO'][dot] == munic_actual:
#                 sub_area += 1
#                 munic_name = '{0}-{1}'.format(df['MUNICIPIO'][dot], sub_area)
#                 print(munic_name)
#                 id_area = db.Area.insert(name=munic_name, description='Ninguna por ahora', id_area_type=2)
#             else:
#                 sub_area = 0
#                 munic_actual = df['MUNICIPIO'][dot]
#                 id_area = db.Area.insert(name=df['MUNICIPIO'][dot], description='Ninguna por ahora', id_area_type=2)
#             print('todo esto es del municipio: {0}'.format(df['MUNICIPIO'][dot]))
#
#         dict_to_add['id_area'] = id_area
#         dict_to_add['step'] = df['vertex_part_index'][dot]
#         dict_to_add['lat'] = df['lat'][dot]
#         dict_to_add['lon'] = df['lon'][dot]
#
#         db.AreaNode.insert(**dict_to_add)
# else:
#     print('ya hay datos')
#
# areas = db(db.Area).select(db.Area.id, db.Area.centroid_lat)
#
# for area in areas:
#     if not area.centroid_lat:
#         nodes = db(db.AreaNode.id_area == area.id).select(db.AreaNode.lat,
#                                                           db.AreaNode.lon)
#         _x_list = []
#         _y_list = []
#         for node in nodes:
#             _x_list.append(node.lat)
#             _y_list.append(node.lon)
#         _len = len(nodes)
#         _x = sum(_x_list) / _len
#         _y = sum(_y_list) / _len
#         db(db.Area.id == area.id).update(centroid_lat=_x, centroid_lon=_y)
#         print('terminé de calcular los centroides: latitud {0}, longitud {1}'
#               .format(_x, _y))
