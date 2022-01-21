
def c_index_pluviometer_graphic():
    c_index = db(db.PrecipitationConcentrationIndex_By_Pluviometer.id > 0).select()
    graphic_type = request.args(0)
    return locals()


def select_graphic():
    page = request.args(0)
    return locals()

