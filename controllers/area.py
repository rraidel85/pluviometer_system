def area_list():
    """Returns all areas that are not sub_areas"""
    areas = db((db.Area.sub_name=="") | (db.Area.sub_name==None)).select()
    area_types = db(db.AreaType.id > 0).select(db.AreaType.id, db.AreaType.name)
    return locals()

def create_area():
    return locals()

def edit_area():
    area_types = db(db.AreaType.id > 0).select(db.AreaType.id, db.AreaType.name)
    return dict(area_types=area_types, areas=__getAreaNodes())


def remove_area():
    area = db.Area(request.args(0, cast=int)) or redirect(URL('area_list'))
    area_id = area.id
    db(db.Area.id == area_id).delete()
    plugin_toastr_message_config('success','Área eliminada correctamente')
    redirect(URL("area_list"))

    return dict()

def area_form():
    form = SQLFORM(db.Area)
    is_editing = False

    if request.args(0):
        area = db.Area(request.args(0, cast=int))
        form = SQLFORM(db.Area, area)
        is_editing = True

    if form.process().accepted:
        response.js = "jQuery('#area_modal').modal('hide');showMyNotification('success', 'Operación realizada exitosamente');updateTable();"
    elif form.errors:
        plugin_toastr_message_config('error', T('Existen errores en el formulario'))

    return dict(form=form, is_editing=is_editing)

def area_form_map():
    areas_without_position = db(db.AreaNode.id_area == None).select(db.Area.id, db.Area.name,
                                                left=db.AreaNode.on(db.Area.id == db.AreaNode.id_area))
    options = []

    for area in areas_without_position:
        options.append(OPTION(area.name, _value=area.id))

    select = SELECT(*options, _id='area-select',
                    _name='area-select', _class='form-control')

    form = SQLFORM(db.Area)

    if form.validate():
        area_id = db.Area.insert(**form.vars)
        response.js = "jQuery('#area_modal').modal('hide');outerSaveAreaPosition(%d);" % area_id
    elif form.errors:
        plugin_toastr_message_config('error', T('Existen errores en el formulario'))

    return dict(form=form, select=select)
#-----------------------------------------------------
# APIS
#-----------------------------------------------------

@request.restful()
def areas_api():
    """Return asynchronous areas data for Datatable"""
    response.view = 'generic.json'

    def GET(*args, **kwargs):
        start = int(request.vars.start)
        limit = int(request.vars.limit)
        search = request.vars.search
        order_column = request.vars.order_column
        order_dir = request.vars.order_dir

        areas = []
        count = 0

        try:
            areas = db(((db.Area.sub_name=="") | (db.Area.sub_name==None)) &
                              (db.Area.name.contains(search))).select(
                        orderby=f'{db.Area[order_column]} {order_dir}',
                        limitby=(start, start+limit))

            count_query = db.Area.id.count()
            count = db(((db.Area.sub_name=="") | (db.Area.sub_name==None)) &
                        (db.Area.name.contains(search))).select(count_query,
                                                                       cache=(cache.ram, None),cacheable=True).first()[count_query]

            for area in areas:
                area.id_area_type = area.id_area_type.name

        except Exception as e:
            print(e)

        data = {
            'length': count,
            'areas': areas.as_list(),
        }

        return data

    return locals()

@request.restful()
def save_area_position_api():
    """Save an area created by the user to the map"""
    response.view = 'generic.json'

    def POST(*args, **kwargs):
        area_id = request.vars.area_id
        points = request.vars.points # Has the form of [[{}, {}]]

        for step,point in enumerate(points[0]):
            db.AreaNode.insert(id_area=area_id,lat=point['lat'],lon=point['lng'],step=step)

        db.commit()

        cache.ram('areas', None) #emptying map cache so that the new areas are shown
        __getAreaNodes() #calling map cache again

        return dict(areaId=area_id)

    return locals()

@request.restful()
def edit_area_position_api():
    """Save area edited by the user to the database"""
    response.view = 'generic.json'

    def POST(*args, **kwargs):
        area_id = request.vars.area_id

        points = request.vars.points # Has the form of [[{}, {}]]
        for step,point in enumerate(points[0]):
            db((db.AreaNode.id_area==area_id) & (db.AreaNode.step==step)).update(lat=point['lat'], lon=point['lng'])

        cache.ram('areas', None)  # emptying map cache so that the new areas are shown
        __getAreaNodes()  # calling map cache again

        db.commit()

        return dict()

    return locals()

@request.restful()
def remove_area_api():
    """Remove area by its id"""
    response.view = 'generic.json'

    def POST(*args, **kwargs):
        area_id = request.vars.area_id
        db(db.Area.id == area_id).delete()
        db.commit()

        cache.ram('areas', None) #emptying map cache so that the new areas are shown
        __getAreaNodes() #calling map cache again

        return dict()

    return locals()