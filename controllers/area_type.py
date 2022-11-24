def areatype_list():
    area_types = db(db.AreaType.id > 0).select()
    return locals()

def remove_areatype():
    areatype = db.AreaType(request.args(0, cast=int)) or redirect(URL('not_found'))
    db(db.AreaType.id == areatype.id).delete()
    plugin_toastr_message_config('success','Operación realizada exitosamente')
    redirect(URL("areatype_list"))

    return dict()

def areatype_form():
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


# def create_areatype():
#     return locals()
#
# def edit_areatype():
#     area_types = db(db.AreaType.id > 0).select(db.AreaType.id, db.AreaType.name)
#     return dict(area_types=area_types, areas=__getAreaNodes())