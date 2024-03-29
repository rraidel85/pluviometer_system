@auth.requires(lector_role, otherwise=URL('user', 'no_autorizado'))
def areatype_list():
    area_types = db(db.AreaType.id > 0).select()
    return locals()

@auth.requires(editor_role, otherwise=URL('user', 'no_autorizado'))
def remove_areatype():
    areatype = db.AreaType(request.args(0, cast=int)) or redirect(URL('not_found'))
    db(db.AreaType.id == areatype.id).delete()
    plugin_toastr_message_config('success','Operación realizada exitosamente')
    redirect(URL("areatype_list"))

    return dict()

def areatype_form():
    form = SQLFORM(db.AreaType)
    is_editing = False
    color = "#000000"

    if request.args(0):
        area_type = db.AreaType(request.args(0, cast=int))
        form = SQLFORM(db.AreaType, area_type)
        color = area_type.representation
        is_editing = True

    if form.process().accepted:
        session.page_reload = True
        redirect(request.env.http_web2py_component_location, client_side=True)
    elif form.errors:
        plugin_toastr_message_config('error', T('Existen errores en el formulario'))

    return dict(form=form, is_editing=is_editing, color=color)
