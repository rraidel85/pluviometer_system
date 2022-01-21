
def yearStatistics():
    """Expect a pluviometer id and return its year statistics(the datatable calls 'yearStatistics_api')"""
    pluv_id = request.args(0, cast=int) or redirect(URL('default', 'index'))
    pluv = db.Pluviometer(pluv_id)
    return locals()


#-----------------------------------------------
# APIS
#-----------------------------------------------
@request.restful()
def years():
    """Return data for map markers (Exercise from Enrique)"""
    response.view = 'generic.json'

    def GET(*args, **kwargs):
        pluv_id = request.vars.id
        resul = db(db.YearStatistics.id_pluviometer==pluv_id).select(db.YearStatistics.year_number.min()
                                                                   ,db.YearStatistics.year_number.max()).first()
        min = resul[db.YearStatistics.year_number.min()]
        max = resul[db.YearStatistics.year_number.max()]

        total_years = max - min
        return dict(min=min, max=max, total_years=total_years)

    return locals()



@request.restful()
def year_statistics_api():
    """Return asynchronous year statistics data for Datatable based on a pluviometer id"""
    response.view = 'generic.json'

    def GET(*args, **kwargs):
        start = int(request.vars.start)
        limit = int(request.vars.limit)
        search = request.vars.search
        order_column = request.vars.order_column
        order_dir = request.vars.order_dir
        pluv_id = request.vars.pluv_id

        stats = []
        count = 0
        try:
            stats = db((db.YearStatistics.id_pluviometer == pluv_id) &
                              (db.YearStatistics.year_number.like(f'%{search}%'))).select(
                                orderby=f'{db.YearStatistics[order_column]} {order_dir}',
                                limitby=(start,start+limit)).as_list()

            count_query = db.YearStatistics.id.count()
            count = db((db.YearStatistics.id_pluviometer == pluv_id) &
                       (db.YearStatistics.year_number.like(f'%{search}%'))).select(count_query,
                                                                                   cache=(cache.ram, None),cacheable=True).first()[count_query]
            print(count)
        except Exception as e:
            print(e)

        data = {
            'length': count,
            'stats': stats
        }

        return data

    return locals()






def index():
    response.flash = T("Hello World, ahora sí")
    grid = SQLFORM.smartgrid(db.YearStatistics,
                             searchable=False,
                             csv=False,
                             showbuttontext=False,
                             paginate=False
                             )
    return locals()