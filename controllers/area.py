def area_list():
    """Returns all areas that are not sub_areas"""
    areas = db((db.Area.sub_name=="") | (db.Area.sub_name==None)).select()
    area_types = db(db.AreaType.id > 0).select(db.AreaType.id, db.AreaType.name)
    return locals()

def create_area():
    area_types = db(db.AreaType.id > 0).select(db.AreaType.id, db.AreaType.name)
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
    reload_table = False

    if form.process().accepted:
        # redirect(request.env.http_web2py_component_location, client_side=True)
        reload_table = True
        response.js = "jQuery('#area_modal').modal('hide');showMyNotification('success', 'El área se ha creado correctamente');"
    elif form.errors:
        plugin_toastr_message_config('error', T('Existen errores en el formulario'))

    return dict(form=form, reload_table=reload_table)

#-----------------------------------------------------
# APIS
#-----------------------------------------------------
@request.restful()
def save_area_api():
    """Save an area created by the user to the map"""
    response.view = 'generic.json'

    def POST(*args, **kwargs):
        name = request.vars.name
        description = request.vars.description
        area_type_id = request.vars.area_type_id
        points = request.vars.points # Has the form of [[{}, {}]]

        new_area = db.Area.insert(name=name,id_area_type=area_type_id,description=description)

        for step,point in enumerate(points[0]):
            db.AreaNode.insert(id_area=new_area,lat=point['lat'],lon=point['lng'],step=step)

        db.commit()

        cache.ram('areas', None) #emptying map cache so that the new areas are shown
        __getAreaNodes() #calling map cache again

        return dict(areaId=new_area)

    return locals()

@request.restful()
def edit_area_api():
    """Save area edited by the user to the database"""
    response.view = 'generic.json'

    def POST(*args, **kwargs):
        edit_type = request.vars.edit_type  # Type of edit: if is 'position' edit the area map position and if is 'information' edit area info
        area_id = request.vars.area_id

        if edit_type == 'position':
            points = request.vars.points # Has the form of [[{}, {}]]
            for step,point in enumerate(points[0]):
                db((db.AreaNode.id_area==area_id) & (db.AreaNode.step==step)).update(lat=point['lat'], lon=point['lng'])

            cache.ram('areas', None)  # emptying map cache so that the new areas are shown
            __getAreaNodes()  # calling map cache again

        elif edit_type == 'information':
            db(db.Area.id == area_id).update(**request.vars)

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