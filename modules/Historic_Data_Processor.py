import pickle

class Historic_Data_Processor:
    def __init__(self, file_route='historic_data.pkl'):
        self.full_data_dict = {}
        with open(file_route, 'rb') as saved_file:
            self.full_data_dict = pickle.load(saved_file)
        print('done loading')

    def get_pluviometers_names(self):
        pluviometer_names = self.full_data_dict.keys()
        return list(pluviometer_names)

    def get_years_registered(self, pluviometer):
        years_registered = self.full_data_dict[pluviometer].keys()
        return list(years_registered)

    def get_year_statistics(self, pluviometer, year):
        return self.full_data_dict[pluviometer][year]

    def getPluviometerData(self, pluviometer_name):
        return self.full_data_dict[pluviometer_name]

    # def LocalTest(self):
    # import os
    #     dir = os.getcwd()
    #     with os.scandir(dir) as it:
    #         for entry in it:
    #             print(entry.name)