def pluv_list():
    """Returns pluviometer table"""
    return locals()

def create_pluv():
    areas = __getAreaNodes()
    return locals()

def edit_pluv():
    pluvs = db(db.Pluviometer.lat > 0).select()
    return dict(areas=__getAreaNodes(), pluvs= pluvs)

def remove_pluv():
    pluv = db.Pluviometer(request.args(0, cast=int)) or redirect(URL('pluv_list'))
    pluv_id = pluv.id
    db(db.Pluviometer.id == pluv_id).delete()
    plugin_toastr_message_config('success','Pluviómetro eliminado correctamente')
    redirect(URL("pluv_list"))

    return dict()

def pluv_by_area():
    area = db.Area(request.args(0, cast=int)) or redirect('error') #la página error todavia no existe
    area_pluvs = db(db.Pluviometer_Area.id_area==area.id).select(db.Pluviometer_Area.id_pluviometer)
    return locals()

def pluv_form():
    form = SQLFORM(db.Pluviometer)
    is_editing = False

    if request.args(0):
        pluv = db.Pluviometer(request.args(0, cast=int))
        form = SQLFORM(db.Pluviometer, pluv)
        is_editing = True

    if form.process().accepted:
        response.js = "jQuery('#pluv_modal').modal('hide');showMyNotification('success', 'Operación realizada exitosamente');updateTable();"
    elif form.errors:
        plugin_toastr_message_config('error', T('Existen errores en el formulario'))

    return dict(form=form, is_editing=is_editing)

def pluv_form_map():
    pluvs_without_position = db((db.Pluviometer.lat==None) | (db.Pluviometer.lon==None)).select()
    options = []

    for pluv in pluvs_without_position:
        options.append(OPTION(pluv.name, _value=pluv.id))

    select = SELECT(*options, _id='pluv-select',
                    _name='pluv-select', _class='form-control')

    create_form = SQLFORM(db.Pluviometer)

    if create_form.validate():
        pluv_id = db.Pluviometer.insert(**create_form.vars)
        response.js = "jQuery('#pluv_modal').modal('hide');outerSavePluviometerPosition(%d);" % pluv_id
    elif create_form.errors:
        plugin_toastr_message_config('error', T('Existen errores en el formulario'))

    return dict(create_form=create_form, select=select)

#-----------------------------------------------
# APIS
#-----------------------------------------------

@request.restful()
def pluvs():
    """Return asynchronous pluviometer data for Datatable"""
    response.view = 'generic.json'

    def GET(*args, **kwargs):
        start = int(request.vars.start)
        limit = int(request.vars.limit)
        search = request.vars.search
        order_column = request.vars.order_column
        order_dir = request.vars.order_dir

        pluviometers = []
        count = 0
        try:
            pluviometers = db((db.Pluviometer.id > 0) &
                              (db.Pluviometer.name.contains(search)) | (db.Pluviometer.station_name.contains(search)) ).select(
                        orderby=f'{db.Pluviometer[order_column]} {order_dir}',
                        limitby=(start, start+limit)).as_list()

            count_query = db.Pluviometer.id.count()
            count = db((db.Pluviometer.id > 0) &
                        (db.Pluviometer.name.contains(search) | (db.Pluviometer.station_name.contains(search)))).select(count_query,
                                                                       cache=(cache.ram, None),cacheable=True).first()[count_query]

        except Exception as e:
            print(e)

        data = {
            'length': count,
            'pluvs': pluviometers
        }

        return data

    return locals()

@request.restful()
def save_pluv_position_api():
    """Save pluviometer position created by the user on the map"""
    response.view = 'generic.json'

    def POST(*args, **kwargs):
        pluv_id = request.vars.pluv_id
        points = request.vars.points
        db(db.Pluviometer.id == pluv_id).update(lat=points['lat'], lon=points['lng'])

        db.commit()

        cache.ram('areas', None) #emptying map cache so that the new pluvs are shown
        __getAreaNodes() #calling map cache again

        return dict(pluvId=pluv_id)

    return locals()


@request.restful()
def edit_pluv_position_api():
    """Save pluviometer edited by the user to the database"""
    response.view = 'generic.json'

    def POST(*args, **kwargs):
        pluv_id = request.vars.pluv_id
        points = request.vars.points

        db(db.Pluviometer.id == pluv_id).update(lat=points['lat'], lon=points['lng']) # Edit pluviometer lat and lon in db

        db.commit()

        cache.ram('areas', None)  # emptying map cache so that the new areas are shown
        __getAreaNodes()  # calling map cache again

        return dict()

    return locals()

@request.restful()
def remove_pluv_api():
    """Remove pluviometer by its id"""
    response.view = 'generic.json'

    def POST(*args, **kwargs):
        pluv_id = request.vars.pluv_id
        db(db.Pluviometer.id == pluv_id).delete()
        db.commit()

        cache.ram('areas', None) #emptying map cache so that the new areas are shown
        __getAreaNodes() #calling map cache again

        return dict()

    return locals()