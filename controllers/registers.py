def registers_list():
    """Returns Registers table"""
    return locals()



def registers_pluv():
    """Expect a pluviometer id and return its registers(the datatable calls 'registers_api')"""
    pluv_id = request.args(0, cast=int) or redirect('error') #la pagina error no existe todavía
    pluv_name = db.Pluviometer(pluv_id).name
    return locals()

def registers_form():
    form = SQLFORM(db.Registers)
    is_editing = False
    register_date = None
    current_page = "registers_pluv" if request.vars.pluv_id else "registers_list"

    if request.args(0):
        register = db.Registers(request.args(0, cast=int))
        form = SQLFORM(db.Registers, register)
        register_date = register.register_date
        is_editing = True

    if request.vars.pluv_id:
        form.vars.id_pluviometer = request.vars.pluv_id

    if form.process().accepted:
        response.js = "jQuery('#registers_modal').modal('hide');showMyNotification('success', 'Operación realizada exitosamente');updateTable();"
    elif form.errors:
        plugin_toastr_message_config('error', T('Existen errores en el formulario'))

    return dict(form=form, is_editing=is_editing,
                register_date=register_date, current_page=current_page)

#-----------------------------------------------
# APIS
#-----------------------------------------------
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

        except Exception as e:
            print(e)

        data = {
            'length': count,
            'registers': registers
        }

        return data

    return locals()

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
                                limitby=(start,start+limit))

            count_query = db.Registers.id.count()
            count = db((db.Registers.id > 0) &
                       (db.Registers.register_date.like(f'{search}%'))).select(count_query,
                                                                               cache=(cache.ram, None),cacheable=True).first()[count_query]

            for register in registers:
                register.id_pluviometer = register.id_pluviometer.name

        except Exception as e:
            print(e)

        data = {
            'length': count,
            'registers': registers.as_list()
        }

        return data

    return locals()


