# Controlador para gestionar los usuarios y permisos

# validadores y set de usuarios
if auth.user:
    usuarios = db(db.auth_user.id != auth.user.id)

require_username = [IS_NOT_EMPTY(error_message="El campo Usuario no puede estar vacío"), IS_NOT_IN_DB(
        db, "auth_user.username",error_message="Ese nombre de usuario ya existe"), IS_LENGTH(20,error_message="El usuario debe tener máximo 20 carácteres")]
require_email = [IS_EMAIL(error_message="Correo inválido"), IS_NOT_IN_DB(db, "auth_user.email",error_message="Ese correo ya existe")]


def login():
    form = SQLFORM.factory(
        Field('username', requires=IS_NOT_EMPTY()),
        Field('password', 'password', requires=[IS_NOT_EMPTY(), CRYPT()]),
    )

    if form.process(hideerror=True).accepted:
        username = form.vars.username
        password = form.vars.password
        user = auth.login_bare(username, password)

        if user:
            plugin_toastr_message_config('success', T(
                'Bienvenido al sistema: ' + username))
            redirect(auth.settings.login_next)
        else:
            form.errors.credenciales = T('Credenciales incorrectas')
            plugin_toastr_message_config('error', T(
                'Usuario o contraseña incorrectos'))
    elif form.errors:
        plugin_toastr_message_config('error', T(
            'Existen errores en el formulario'))

    return dict(form=form)

def registro():
    form = SQLFORM.factory(
        Field("first_name", requires=IS_NOT_EMPTY(error_message='El campo Nombre no puede estar vacio')),
        Field("last_name", requires=IS_NOT_EMPTY(error_message='El campo Apellidos no puede estar vacio')),
        Field("username", requires=require_username),
        Field("email", requires=require_email),
        Field("password", "password",
              requires=[IS_NOT_EMPTY(error_message='El campo Contraseña no puede estar vacio'), CRYPT()]),
        Field("repeat", "password",requires=[IS_EQUAL_TO(request.vars.password,
                                                         error_message='Las contraseñas deben coincidir')]))

    if form.process(hideerror=True).accepted:
        user_id = db.auth_user.insert(**form.vars)
        # db.auth_membership.insert(
        #     user_id=user_id, group_id=form.vars.rol)
        auth.login_bare(form.vars.username,form.vars.password)

        # By default new users will belong to the 'lector' group
        group_id = auth.id_group('lector')
        auth.add_membership(group_id, user_id)

        plugin_toastr_message_config('success', T(
            'Bienvenido al sistema: ' + auth.user.username))
        redirect(auth.settings.login_next)
    elif form.errors:
        first_error = list(form.errors.values())[0]
        plugin_toastr_message_config('error',first_error)

    return dict(form=form)

# Cierra la sesión del usuario dado
@auth.requires_login()
def logout():
    auth.logout()
    return dict()


# Url para mostrar mensaje de NO autorizado
@auth.requires_login()
def no_autorizado():
    return locals()

# Url para mostrar mensaje de NO autorizado
@auth.requires_login()
def no_encontrado():
    return locals()

# Opcion para editar perfil si el usuario no es admin
@auth.requires_login()
def editar_perfil():
    registro = db.auth_user(auth.user.id) or redirect(URL('default', 'index'))

    if registro.username == "admin":
        session.status = True
        session.msg = "El usuario admin no puede editar su perfil"
        redirect(URL("default", "index"))

    form = SQLFORM.factory(
        Field("first_name", label=T("Nombre(s)"), default=registro.first_name, requires=IS_NOT_EMPTY()),
        Field("last_name", label=T(
            "Apellidos"), default=registro.last_name, requires=IS_NOT_EMPTY()),
        Field("username", label=T("Nombre de usuario"),
              default=registro.username, requires=require_username),
        Field("email", label=T("Correo electrónico"),
              default=registro.email, requires=require_email),
        )

    if form.validate():
        db(db.auth_user.id == registro.id).update(**form.vars)
        session.status = True
        session.msg = 'Usuario actualizado correctamente'
        redirect(URL("perfil"))
    elif form.errors:
        session.error = True
        session.msg = 'El formulario tiene errores'
    return dict(form=form)


# -------------------------------------------------------------------------
# Administrador
# -------------------------------------------------------------------------

# Devuelve listado de usuarios y su rol, excepto el admin
@auth.requires(admin_role, otherwise=URL('user', 'no_autorizado'))
def user_list():
    users = db((db.auth_user.id != auth.user.id) & (db.auth_user.username != "admin")
              & (db.auth_membership.user_id == db.auth_user.id)).select(db.auth_user.ALL, db.auth_membership.ALL)

    return locals()

@auth.requires(admin_role, otherwise=URL('user', 'no_autorizado'))
def remove_user():
    user = db.auth_user(request.args(0, cast=int)) or redirect(URL('not_found'))
    db(db.auth_user.id == user.id).delete()
    plugin_toastr_message_config('success', 'Operación realizada exitosamente')
    redirect(URL("user_list"))

    return dict()

# Devuelve informacion sobre el usuario logueado actualmente
@auth.requires_login()
def perfil():
    usuario = db.auth_user(auth.user.id) or redirect(URL('default', 'index'))

    rol = db(db.auth_membership.user_id ==
             usuario.id).select().first().group_id.role

    return locals()


# Devuelve información sobre un usuario seleccionado por el admin
@auth.requires_membership("Administrador")
def detalles():
    if not request.args(0):
        redirect(URL('default', 'index'))

    usuario = db.auth_user(request.args(0, cast=int)
                           ) or redirect(URL('administrar'))

    rol = db(db.auth_membership.user_id ==
             usuario.id).select().first().group_id.role

    return locals()


def user_form():
    user_id = None
    usuarios = db(db.auth_user.id > 0)
    require_username = [IS_NOT_EMPTY(error_message='Este campo es obligatorio'), IS_NOT_IN_DB(
        usuarios, "auth_user.username", error_message='Este campo ya existe'),
                        IS_LENGTH(20, error_message='Este campo debe ser menor a 20 caracteres')]
    require_email = [IS_NOT_EMPTY(error_message='Este campo es obligatorio'), IS_EMAIL(error_message='Este campo debe ser un correo válido'
    ), IS_NOT_IN_DB(usuarios, "auth_user.email", error_message='Este campo ya existe')]
    is_editing = False

    form = SQLFORM.factory(Field("first_name", label=T("Nombre(s)"),
                                 requires=IS_NOT_EMPTY(error_message='Este campo es obligatorio')),
                           Field("last_name", label=T("Apellidos"),
                                 requires=IS_NOT_EMPTY(error_message='Este campo es obligatorio')),
                           Field("username", label=T(
                               "Nombre de usuario"), requires=require_username),
                           Field("email", label=T("Correo electrónico"),
                                 requires=require_email),
                           Field("password", "password", label=T(
                               "Contraseña"), requires=[IS_NOT_EMPTY(error_message='Este campo es obligatorio'), CRYPT()]),
                           Field("repeat", "password", label=T("Repetir contraseña"), requires=[
                               IS_EQUAL_TO(request.vars.password, error_message='Este campo debe ser igual a la contraseña')]),
                           Field("role", "reference auth_group", label=T("Rol de usuario"),
                                 requires=IS_IN_DB(db, 'auth_group.id', '%(role)s', error_message='Seleccione un rol válido',
                                                   zero=T('Seleccionar rol'))),
                           )

    # FORM EDIT
    if request.args(0):
        is_editing = True
        user_id = request.args(0, cast=int)
        user = db(db.auth_user.id == user_id).select().first()
        role_id = db(db.auth_membership.user_id == user_id).select().first().group_id.id

        form = SQLFORM.factory(Field("first_name", label=T("Nombre(s)"),
                                     requires=IS_NOT_EMPTY(error_message='Este campo es obligatorio'), default=user.first_name,),
                               Field("last_name", label=T("Apellidos"), default=user.last_name,
                                     requires=IS_NOT_EMPTY(error_message='Este campo es obligatorio')),
                               Field("username", label=T(
                                   "Nombre de usuario"), default=user.username,
                                     requires=[IS_NOT_EMPTY(error_message='Este campo es obligatorio'),
                                               IS_LENGTH(20,
                                                        error_message='Este campo debe ser menor a 20 caracteres')]),
                               Field("email", label=T("Correo electrónico"), default=user.email,
                                     requires=IS_NOT_EMPTY(error_message='Este campo es obligatorio')),
                               Field("role", "reference auth_group", label=T("Rol de usuario"), default=role_id,
                                     requires=IS_IN_DB(db, 'auth_group.id', '%(role)s',
                                                        error_message='Seleccione un rol válido',
                                                       zero=T('Seleccionar rol'))),
                               )


    if form.validate():
        if not is_editing: #If is on create mode
            user_id = db.auth_user.insert(**form.vars)
            db.auth_membership.insert(user_id=user_id, group_id=form.vars.role)
        else: #If is on edit mode
            db(db.auth_user.id == user_id).update(**form.vars)
            db(db.auth_membership.user_id == user_id).update(
                group_id=form.vars.role)

        session.page_reload = True
        redirect(request.env.http_web2py_component_location, client_side=True)
    elif form.errors:
        plugin_toastr_message_config('error', T('Existen errores en el formulario'))

    return dict(form=form, is_editing=is_editing)


# Actualiza la contraseña del usuario logueado
@auth.requires_login()
def change_password():
    registro = db.auth_user(auth.user.id) or redirect(URL('default', 'index'))

    form = SQLFORM.factory(
        Field("password", "password", label=T("Nueva Contraseña"), requires=[IS_NOT_EMPTY(), CRYPT()]),
        Field("repeat", "password", label=T("Repetir contraseña"), requires=[
            IS_EQUAL_TO(request.vars.password)]),
        )

    if form.validate():
        db(db.auth_user.id == registro.id).update(**form.vars)
        session.pass_changed = True
        redirect(URL("default", 'index'))
    elif form.errors:
        plugin_toastr_message_config('error', T('Existen errores en el formulario'))

    return dict(form=form, registro=registro)


# Cambia como admin la contraseña de un usuario dado
@auth.requires_membership("Administrador")
def cambiar_clave_usuario():
    if not request.args(0):
        redirect(URL('default', 'index'))

    registro = db.auth_user(request.args(0, cast=int)
                            ) or redirect(URL('administrar'))

    form = SQLFORM.factory(
        Field("password", "password", label=T("Nueva Contraseña"), requires=[IS_NOT_EMPTY(), CRYPT()]),
        Field("repeat", "password", label=T("Repetir contraseña"), requires=[
            IS_EQUAL_TO(request.vars.password)]),
        )

    if form.validate():
        db(db.auth_user.id == registro.id).update(**form.vars)
        session.status = True
        session.msg = 'Contraseña actualizada correctamente'
        redirect(URL("detalles", args=registro.id))
    elif form.errors:
        session.error = True
        session.msg = 'El formulario tiene errores'

    return dict(form=form, registro=registro)




