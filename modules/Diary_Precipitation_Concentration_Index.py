# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import scipy.integrate as integrate


class Diary_Precipitation_Concentration_Index:
    """
    Clase para calcular coeficiente de concentración temporal diaria
    """

    def __init__(self, precip_data, file_name):
        self.info_on_a_row = pd.Series(precip_data)
        self.file_name = file_name
        self.max_registered_value = self.info_on_a_row.max()
        self.sum_registered_values = self.info_on_a_row.sum()
        classes_inf_limit = list(np.arange(0, self.max_registered_value, 1))

        self.df = pd.DataFrame(classes_inf_limit, columns=(['bottom_limit']))
        # self.df['upper_limit'] = self.df.apply(lambda x: x + 0.99)
        self.df[['PM', 'ni', 'Pi']] = self.df.apply(self.sum_count_PM_precip_per_class, axis=1).tolist()

        # Borro todas las filas que no tengan registros de lluvias diarias en la clase en cuestión
        self.df.drop(self.df[self.df.ni == 0].index, inplace=True)

        self.cumulative_freq_stacked_sum_ni_and_Pi = self.get_cumulative_freq_stacked_sum_ni_and_Pi()
        self.df['cumulative_freq_stacked_sum_ni'] = self.cumulative_freq_stacked_sum_ni_and_Pi[0]
        self.df['cumulative_freq_stacked_sum_Pi'] = self.cumulative_freq_stacked_sum_ni_and_Pi[1]

        self.total_sum_ni = self.df['ni'].sum()
        self.df['cumulative_percentage_of_rainy_days_ni_X'] = self.df['cumulative_freq_stacked_sum_ni'].apply(
            lambda x: x * 100 / self.total_sum_ni)

        self.total_sum_Pi = self.df['Pi'].sum()
        self.df['cumulative_percentage_of_rainfall_amounts_Pi_Y'] = self.df['cumulative_freq_stacked_sum_Pi'].apply(
            lambda x: x * 100 / self.total_sum_Pi)
        self.pars_exp, self.cov_exp = self.adjust_curve_from_data()

        self.xnew = np.linspace(start=0, stop=100, num=500)
        self.ynew_exidist = self.xnew
        self.ynew_exp = self.exp_function_to_fit(self.xnew, *self.pars_exp)
        self.ci = self.calculate_ci()

        self.y_original = self.df['cumulative_percentage_of_rainfall_amounts_Pi_Y']
        self.y_stimated = self.exp_function_to_fit(self.df['cumulative_percentage_of_rainy_days_ni_X'], *self.pars_exp)
        self.R_2 = pow(np.corrcoef(self.y_original, self.y_stimated)[0, 1], 2)
        # self.plot_function()

    def sum_count_PM_precip_per_class(self, limits):
        mask = self.info_on_a_row.apply(lambda x: limits['bottom_limit'] < x <= limits['bottom_limit'] + 1 and x != 0)
        PM = (limits['bottom_limit'] + limits['bottom_limit'] + 1) / 2
        Pi_bruto = self.info_on_a_row[mask].sum()
        ni = mask.sum()
        Pi_metodol = PM * ni
        return PM, ni, Pi_metodol

    def get_cumulative_freq_stacked_sum_ni_and_Pi(self):
        cumulative_freq_stacked_sum_ni = [0]
        cumulative_freq_stacked_sum_Pi = [0]
        for index in self.df.index:
            cumulative_freq_stacked_sum_ni.append(self.df.at[index, 'ni'] + cumulative_freq_stacked_sum_ni[-1])
            cumulative_freq_stacked_sum_Pi.append(self.df.at[index, 'Pi'] + cumulative_freq_stacked_sum_Pi[-1])
        return cumulative_freq_stacked_sum_ni[1:], cumulative_freq_stacked_sum_Pi[1:]

    def adjust_curve_from_data(self):
        pars_exp, cov_exp = curve_fit(f=self.exp_function_to_fit,
                                      xdata=self.df['cumulative_percentage_of_rainy_days_ni_X'],
                                      ydata=self.df['cumulative_percentage_of_rainfall_amounts_Pi_Y'],
                                      p0=(0.5, 0.05))
        # print('Pars exp:', pars_exp)
        return pars_exp, cov_exp

    def exp_function_to_fit(self, x, a, b):
        return a * np.exp(b * x)

    def plot_function(self):
        fig = plt.figure()
        axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])  # left, bottom, width, height (range 0 to 1)
        axes.plot(self.df['cumulative_percentage_of_rainy_days_ni_X'],
                  self.df['cumulative_percentage_of_rainfall_amounts_Pi_Y'],
                  'm+', label="Datos experimentales")
        axes.plot(self.xnew, self.ynew_exp, 'r', label='Función exponencial ajustada')
        axes.plot(self.xnew, self.ynew_exidist, 'b', label='Recta de equidistribución')
        axes.fill_between(self.xnew, self.ynew_exp, self.ynew_exidist,
                          alpha=0.5)  # representación gráfica de S'=5000-A'

        axes.set_title("Coeficiente de concentración diaria: {0}".format(self.ci))
        axes.set_xlabel \
            ('cumulative Sum Ni (%)')
        axes.set_ylabel('cumulative Sum Pi (%)')

        function = ('y={0}*exp({1}x)'
                    .format(round(self.pars_exp[0], 3), round(self.pars_exp[1], 3)))

        from matplotlib.offsetbox import AnchoredText
        at = AnchoredText('f(x)={0}\n R^2 = {1}'
                          .format(function, round(self.R_2, 4)),
                          prop=dict(size=9, color='m'), frameon=True, loc='lower right')
        at.patch.set_boxstyle("round,pad=0.,rounding_size=0.3")
        axes.add_artist(at)
        axes.text(40, 30, "S' = 5000-A'")
        axes.legend()
        # fig.savefig(fname=self.file_name + '.svg', format="svg")
        fig.savefig(fname=self.file_name + '.png', dpi=250, format="png")
        # fig.show()

    def calculate_ci(self):
        # result = integrate.quad(lambda x: self.exp_function_to_fit(x, *self.pars_exp), 0, 100)
        area_bajo_curva_ajustada = integrate.simpson(self.ynew_exp, self.xnew)
        area_intermedia_entre_equidist_y_curva_ajustada = 5000 - area_bajo_curva_ajustada
        # print('area_bajo_curva_ajustada')
        # print(area_bajo_curva_ajustada)
        # print('area_intermedia_entre_equidist_y_curva_ajustada')
        # print(area_intermedia_entre_equidist_y_curva_ajustada)
        return area_intermedia_entre_equidist_y_curva_ajustada / 5000


# file_route = ''
# resume_df = pd.DataFrame()
# pluviometer_data = pd.read_csv('años registrados por pluviómetro cuenca Chambas.csv', index_col='id_pluviometer')
# total_registered_months = pluviometer_data['years considered'].sum()
# print(total_registered_months)
#
# with pd.ExcelWriter('output.xlsx') as writer:
#     for month in range(12):
#         file_route = 'Para artículo por meses\mes ' + str(month + 1)
#         month_data = pd.read_csv(file_route + '.csv')
#         ci_calculator = Diary_Precipitation_Concentration_Index(month_data['Registro'], file_route)
#         ci_calculator.plot_function()
#         ci_calculator.df.to_excel(writer, sheet_name='mes ' + str(month + 1))
#         resume_df = resume_df.append(pd.DataFrame([[
#             ci_calculator.pars_exp[0],  # a
#             ci_calculator.pars_exp[1],  # b
#             round(ci_calculator.R_2, 4),  # R^2
#             round(ci_calculator.ci, 3),  # Coef concentración de precipitaciones
#             round(ci_calculator.df['cumulative_freq_stacked_sum_ni'].iat[-1], 2),  # Total de días con lluvia
#             round(ci_calculator.sum_registered_values, 2),  # Total precipitaciones (aboluto)
#             round(ci_calculator.max_registered_value, 2),  # Máxima precipitación registrada
#             round(ci_calculator.sum_registered_values / total_registered_months, 2),  # Cant promedio de lluvia por mes
#             # Cant promedio de días lluviosos x mes
#             round(ci_calculator.df['cumulative_freq_stacked_sum_ni'].iat[-1] / total_registered_months, 2)
#         ]],
#             columns=['a',
#                      'b',
#                      'R^2',
#                      'Coef concentración',
#                      'Total dias con lluvia (absoluto)',
#                      'Total precipitaciones (absoluto)',
#                      'Máxima precipitación registrada',
#                      'Cant promedio de lluvia x mes',
#                      'Cant Promedio de días lluviosos x mes',
#                      ],
#             index=['mes ' + str(month + 1)]))
#     resume_df.to_excel(writer, sheet_name='Resumen')
#     pluviometer_data.to_excel(writer, sheet_name='Información del origen de datos')
