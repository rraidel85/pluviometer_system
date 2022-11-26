def pluvtype_list():
    pluv_types = db(db.PluviometerType.id > 0).select()
    return locals()

def remove_pluvtype():
    pluvtype = db.PluviometerType(request.args(0, cast=int)) or redirect(URL('not_found'))
    db(db.PluviometerType.id == pluvtype.id).delete()
    plugin_toastr_message_config('success','Operación realizada exitosamente')
    redirect(URL("pluvtype_list"))

    return dict()

def pluvtype_form():
    form = SQLFORM(db.PluviometerType)
    is_editing = False

    if request.args(0):
        pluv_type = db.PluviometerType(request.args(0, cast=int))
        form = SQLFORM(db.PluviometerType, pluv_type)
        is_editing = True

    if form.process().accepted:
        session.page_reload = True
        redirect(request.env.http_web2py_component_location, client_side=True)
    elif form.errors:
        plugin_toastr_message_config('error', T('Existen errores en el formulario'))

    return dict(form=form, is_editing=is_editing)
