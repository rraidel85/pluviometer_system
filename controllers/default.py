

"""
Ficticious data for testing purposes
The data corresponds with the Pluviometer table in terms of 'name' and 'id'
"""

def __calculate_time():
    print(f"Query:{db._timings[-1][0]}")
    print(f"Time:{db._timings[-1][1] * 1000}")


@auth.requires_login()
def index():
    cant_pluvs = db(db.Pluviometer.id>0).count()
    cant_areas = db((db.Area.sub_name == "") | (db.Area.sub_name == None)).count()
    return locals()

def tabla():
    """Created only for testing purposes, same as default/index"""
    return locals()


#-----------------------------------------------
# APIS
#-----------------------------------------------
@request.restful()
def api():
    """Api that returns test info only for testing purposes"""
    response.view = 'generic.json'

    def GET(*args, **kwargs):
        # print(kwargs['id'])
        # pluv_name = 'CA-60'
        # lat = 21.4206 #pluv.lat
        # lon = -77.8912
        return dict(pluv_name='CA-60', lat=21.4206, lon=-77.8912)

    return locals()


# Default web2py stuff
# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
