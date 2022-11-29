
def monthStatistics():
    """Expect a year id and return its month statistics(the datatable calls 'monthStatistics_api')"""
    year_id = request.args(0, cast=int) or redirect(URL('user', 'no_encontrado'))
    year = db.YearStatistics(year_id)
    return locals()


#-----------------------------------------------
# APIS
#-----------------------------------------------
@request.restful()
def month_statistics_api():
    """Return asynchronous month statistics data for Datatable based on a pluviometer id"""
    response.view = 'generic.json'

    def GET(*args, **kwargs):
        start = int(request.vars.start)
        limit = int(request.vars.limit)
        search = request.vars.search
        order_column = request.vars.order_column
        order_dir = request.vars.order_dir
        year_id = request.vars.year_id

        stats = []
        count = 0
        try:
            stats = db((db.MonthStatistics.id_year == year_id)).select(
                                orderby=f'{db.MonthStatistics[order_column]} {order_dir}',
                                limitby=(start,start+limit))

            count_query = db.MonthStatistics.id.count()
            count = db((db.MonthStatistics.id_year == year_id)).select(count_query,
                                                                                   cache=(cache.ram, None),cacheable=True).first()[count_query]

            for stat in stats:
                stat.month_number = stat.month_number.month_name

        except Exception as e:
            print(e)

        data = {
            'length': count,
            'stats': stats.as_list()
        }

        return data

    return locals()



