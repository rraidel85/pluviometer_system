def area_list():
    """Returns all areas that are not sub_areas"""
    areas = db((db.Area.sub_name=="") | (db.Area.sub_name==None)).select()
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
    plugin_toastr_message_config('success','Area eliminada correctamente')
    redirect(URL("area_list"))

    return dict()

