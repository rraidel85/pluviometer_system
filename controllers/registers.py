def index():
    """Returns Registers table"""
    return locals()



def registers_pluv():
    """Expect a pluviometer id and return its registers(the datatable calls 'registers_api')"""
    pluv_id = request.args(0, cast=int) or redirect('error') #la pagina error no existe todavía
    pluv_name = db.Pluviometer(pluv_id).name
    return locals()



#-----------------------------------------------
# APIS
#-----------------------------------------------
@request.restful()
def registers_api():
    """Return asynchronous registers data for the Datatable"""
    response.view = 'generic.json'

    def GET(*args, **kwargs):
        start = int(request.vars.start)
        limit = int(request.vars.limit)
        search = request.vars.search
        order_column = request.vars.order_column
        order_dir = request.vars.order_dir

        registers = []
        count = 0
        try:
            registers = db((db.Registers.id > 0) &
                              (db.Registers.register_date.like(f'{search}%'))).select(
                                orderby=f'{db.Registers[order_column]} {order_dir}',
                                limitby=(start,start+limit)).as_list()

            count_query = db.Registers.id.count()
            count = db((db.Registers.id > 0) &
                       (db.Registers.register_date.like(f'{search}%'))).select(count_query,
                                                                               cache=(cache.ram, None),cacheable=True).first()[count_query]
            print(count)
        except Exception as e:
            print(e)

        data = {
            'length': count,
            'registers': registers
        }

        return data

    return locals()


@request.restful()
def registers_pluv_api():
    """Return asynchronous registers data for Datatable based on a pluviometer id"""
    response.view = 'generic.json'

    def GET(*args, **kwargs):
        start = int(request.vars.start)
        limit = int(request.vars.limit)
        search = request.vars.search
        order_column = request.vars.order_column
        order_dir = request.vars.order_dir
        pluv_id = request.vars.pluv_id

        registers = []
        count = 0
        try:
            registers = db((db.Registers.id_pluviometer == pluv_id) &
                              (db.Registers.register_date.like(f'{search}%'))).select(
                                orderby=f'{db.Registers[order_column]} {order_dir}',
                                limitby=(start,start+limit)).as_list()

            count_query = db.Registers.id.count()
            count = db((db.Registers.id_pluviometer == pluv_id) &
                       (db.Registers.register_date.like(f'{search}%'))).select(count_query,
                                                                               cache=(cache.ram, None),cacheable=True).first()[count_query]
            print(count)
        except Exception as e:
            print(e)

        data = {
            'length': count,
            'registers': registers
        }

        return data

    return locals()