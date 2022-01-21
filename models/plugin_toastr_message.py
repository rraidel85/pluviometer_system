# Configuracion del plugin
def plugin_toastr_message_config(status, msg, ajax=False):
    session.plugin_toastr_message_msg = msg

    if status == 'success':
        session.plugin_toastr_message_success = True
    elif status == 'error':
        session.plugin_toastr_message_error = True
    elif status == 'warning':
        session.plugin_toastr_message_warning = True
    elif status == 'info':
        session.plugin_toastr_message_info = True

    jquery = "jQuery('#plugin-toastr-message').get(0).reload();"
    if response.js:
        response.js += jquery
    else:
        response.js = jquery

# Inyecta el plugin en la vista


def plugin_toastr_message():
    return LOAD('plugin_toastr_message', 'message', target='plugin-toastr-message', ajax=True)
