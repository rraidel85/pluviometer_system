def pluv_list():
    """Returns pluviometer table"""
    pluv_types = db(db.PluviometerType.id > 0).select()  # for the select box on edit pluviometer modal
    return locals()

def create_pluv():
    pluv_types = db(db.PluviometerType.id > 0).select() #for the select box
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

def pluvs_grid():
    """Made with only purpose of checking if the pluviometers and registers table match with other controllers"""
    form = SQLFORM.smartgrid(db.Pluviometer, linked_tables=['Registers'], csv=dict(Pluviometer=False, Registers=False),
                            searchable=dict(Pluviometer=False,Registers=False),
                             paginate=dict(Pluviometer=False),
                             links=dict(
                                 Pluviometer=[lambda row: A('Ubicación', _class='btn btn-primary',
                                                            _href=URL('mapa',args=row.id))]))
    return locals()


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
def save_pluv_api():
    """Save pluviometer created by the user to the map"""
    response.view = 'generic.json'

    def POST(*args, **kwargs):
        name = request.vars.name
        pluv_type_id = request.vars.pluv_type_id
        station_name = request.vars.station_name
        msnm = request.vars.msnm
        points = request.vars.points
        new_pluv = db.Pluviometer.insert(name=name,id_pluviometer_type=pluv_type_id,station_name=station_name,
                                  msnm=msnm,lat=points['lat'],lon=points['lng'])

        db.commit()

        cache.ram('areas', None) #emptying map cache so that the new areas are shown
        __getAreaNodes() #calling map cache again

        return dict(pluvId=new_pluv)

    return locals()


@request.restful()
def edit_pluv_api():
    """Save pluviometer edited by the user to the database"""
    response.view = 'generic.json'

    def POST(*args, **kwargs):
        edit_type = request.vars.edit_type # Type of edit: if is 'position' edit the pluv map position and if is 'information' edit pluv info
        pluv_id = request.vars.pluv_id

        if edit_type == 'position':
            points = request.vars.points
            db(db.Pluviometer.id == pluv_id).update(lat=points['lat'], lon=points['lng']) # Edit pluviometer lat and lon in db
            cache.ram('areas', None)  # emptying map cache so that the new areas are shown
            __getAreaNodes()  # calling map cache again
        elif edit_type == 'information':
            name = request.vars.name
            pluv_type_id = request.vars.pluv_type_id
            station_name = request.vars.station_name
            msnm = request.vars.msnm
            db(db.Pluviometer.id == pluv_id).update(name=name, id_pluviometer_type=pluv_type_id,
                                                    station_name=station_name, msnm=msnm)

        db.commit()

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