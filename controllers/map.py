from Dot_In_Polygon import dotInPolygon
from municipios import municipios


def __fillPluviometerTableWithTestData(data):
    for dic in data:
        db(db.Pluviometer.id==dic['id']).update(lat=dic['lat'],lon=dic['lon'])


def __fillPluviometerAreaTable():
    """Fill Pluviometer Area table with the first 13 pluviometers
    Pluviometer location data is still ficticious
    """
    try:
        for row in db(db.Pluviometer.id<=13).select(): # The 13 firts pluviometers

            # for area in db().select(db.Area.id, db.Area.name, db.Area.sub_name): # For every area row in Area table (only selecting 'id' field)
            #     nodes_list = []
            #     area_nodes = db(db.AreaNode.id_area==area.id).select(db.AreaNode.lat,db.AreaNode.lon)
            #     for area_node in area_nodes:#For every area_node(point) in an area
            #         nodes_list.append([area_node.lat,area_node.lon])
            for key in municipios:
                if dotInPolygon(row.lat, row.lon, municipios[key][1]):
                    db.Pluviometer_Area.insert(id_area=municipios[key][0],id_pluviometer=row.id)
                    # print(f'{row["name"]} esta en {area.sub_name if area.sub_name else area.name}')
    except Exception as e:
        print(e)

# def __saveMunicipioNodesInFile():
#     """
#     Get all area nodes for all areas(municipios)
#     Save in a file a diccionary with the following strcuture {'area_name':[area_id, [[areanode_lat],[areanode_lon],...]}
#     """
#     area_borders = {}
#     for area in db().select(db.Area.id, db.Area.name, db.Area.sub_name):
#         key = f'{unidecode.unidecode(area.sub_name.lower()) if area.sub_name else unidecode.unidecode(area.name.lower())}'# Converts the area_name to lower and delete the accents
#         area_borders[key] = [area.id, []]
#         for area_node in db(db.AreaNode.id_area == area.id).select(db.AreaNode.lat, db.AreaNode.lon):
#             area_borders[key][1].append([area_node.lat, area_node.lon])
#
#     f = open('bordes_municipios.txt', 'w')
#     f.write(str(area_borders))
#     f.close()


# @cache('areas', None, cache.ram)
# def __getAreaNodes():
#     """
#     Get all area nodes for all areas
#     Save in a file a diccionary with the following strcuture {'area_name':[area_id, [[areanode_lat],[areanode_lon],...]}
#     """
#     area_borders = {}
#     for area in db().select(db.Area.id, db.Area.id_area_type, db.Area.name, db.Area.sub_name):
#         key = area.sub_name if area.sub_name else area.name
#         area_borders[key] = [area.id, [], area.id_area_type]
#         for area_node in db(db.AreaNode.id_area == area.id).select(db.AreaNode.lat, db.AreaNode.lon):
#             area_borders[key][1].append([area_node.lat, area_node.lon])
#
#     return area_borders


def mapa():
    """Return all pluviometers to the map """

    pluvs = db(db.Pluviometer.lat > 0).select()
    # define_pluviometers_in_areas(pluvs)  #ver definición del método más abajo.

    return dict(areas=__getAreaNodes() ,pluvs=pluvs)


def ubicacion_pluv():
    """Expect a pluviometer id and return its info to the map"""

    pluv_id = request.args(0, cast=int) or redirect(URL('default', 'index'))
    pluv = db.Pluviometer(pluv_id)

    return locals()

def ubicacion_area():
    """Expect a area id and return its info to the map"""

    area_id = request.args(0)
    area = db.Area(area_id)
    sub_areas = list(db(db.Area.name == area.name).select(db.Area.id).as_dict().keys()) # The area and its sub_areas ids
    areas_dict = {}
    area_nodes_array = []
    for id_area in sub_areas:
        sub_area_nodes = db(db.AreaNode.id_area==id_area).select(db.AreaNode.lat, db.AreaNode.lon)
        for area_node in sub_area_nodes:
            # Set in an array the area nodes so that the map can draw it
            area_nodes_array.append([area_node.lat, area_node.lon])
        areas_dict[id_area] = area_nodes_array # area_dict has the form: area_dict={id_area: [[], [], []]}
        area_nodes_array = []
    return dict(area=area,areas_dict=areas_dict)

#-----------------------------------------------------
# APIS
#-----------------------------------------------------
@request.restful()
def marker_mouseover():
    """Shows the areas of the marker(pluviometer)"""
    response.view = 'generic.json'

    def GET(*args, **kwargs):

        ############### Areas
        active_layer_names = request.vars['layers[]'] # Nombre de los tipos de area que estan activas en el mapa

        if active_layer_names:
            area_types_id_list = [] # Guarda todos los ids de los tipos de areas activas en el mapa
            pluv_id = request.vars.id  # id del pluviometro seleccionado

            # Compruebo si es un string o una lista porque si es uno solo me lo manda como un string
            if isinstance(active_layer_names, list):
                for layer in active_layer_names:
                     area_types_id_list.append(db.AreaType(name=layer).id)
            else:
                area_types_id_list.append(db.AreaType(name=active_layer_names).id)

            areas = []
            for pluv_area in db(db.Pluviometer_Area.id_pluviometer == pluv_id).select():
                area = db.Area(pluv_area.id_area)
                if area.id_area_type in area_types_id_list:
                    # Compruebo para cada area del pluv si esta en los tipos de area activos
                    areas.append(area)
        else:
            areas = [' - ']

        ################## Años
        pluv_id = request.vars.id
        resul = db(db.YearStatistics.id_pluviometer == pluv_id).select(db.YearStatistics.year_number.min()
                                                                       , db.YearStatistics.year_number.max()).first()
        min = resul[db.YearStatistics.year_number.min()]
        max = resul[db.YearStatistics.year_number.max()]

        total_years = max - min

        return dict(areas=areas, min=min, max=max, total_years=total_years)

    return locals()

@request.restful()
def area_mouseover():
    """Shows the name and subname of the area"""
    response.view = 'generic.json'

    def GET(*args, **kwargs):
        area_id = request.vars.id
        area = db(db.Area.id == area_id).select(db.Area.name, db.Area.sub_name,
                                                db.Area.description, db.Area.id_area_type).first()
        area_type_name = area.id_area_type.name
        return dict(area=area,area_type_name=area_type_name)

    return locals()


@request.restful()
def nodes():
    """Get all nodes given a certain area id"""
    response.view = 'generic.json'

    def GET(*args, **kwargs):
        area_id = request.vars.id
        area = db.Area(area_id)
        point_nodes = db(db.AreaNode.id_area == area_id).select()
        nodes_array = []
        for node in point_nodes:
            nodes_array.append([node.lat, node.lon])
        # area_dict[area_type.name].append(dict(name=area.name,
        #                             id=area.id,
        #                             description=area.description,
        #                             nodes_array=nodes_array))

        return dict(nodes=nodes_array)

    return locals()


@request.restful()
def save_area_api():
    """Save an area created by the user to the map"""
    response.view = 'generic.json'

    def POST(*args, **kwargs):
        name = request.vars.name
        area_type_id = request.vars.area_type_id
        points = request.vars.points # Has the form of [[{}, {}]]

        new_area = db.Area.insert(name=name,id_area_type=area_type_id)

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
        area_id = request.vars.area_id

        if request.vars.points:
            points = request.vars.points # Has the form of [[{}, {}]]
            for step,point in enumerate(points[0]):
                db((db.AreaNode.id_area==area_id) & (db.AreaNode.step==step)).update(lat=point['lat'], lon=point['lng'])

        if request.vars.name or request.vars.id_area_type:
            db(db.Area.id == area_id).update(**request.vars)

        db.commit()

        cache.ram('areas', None) #emptying map cache so that the new areas are shown
        __getAreaNodes() #calling map cache again

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


#############################################
# Helper Functions
#############################################
def define_pluviometers_in_areas(pluvs):
    """
    Verifica y registra la relación entre un pluviómetros y las áreas que se encuentran definidas por sus nodos
    Args:
        pluvs: lista de pluviómetros
    Returns:

    """
    areas = db(db.Area).select(db.Area.id)
    for pluv in pluvs:
        print(pluv.lat)
        print(pluv.lon)
    for area in areas:
        poligon = db(db.AreaNode.id_area == area.id).select(db.AreaNode.lat, db.AreaNode.lon)
        for_processing = []
        for polig in poligon:
            for_processing.append((polig.lat, polig.lon))

        for pluv in pluvs:
            if db((db.Pluviometer_Area.id_pluviometer == pluv.id) &
                  (db.Pluviometer_Area.id_area == area.id)).count() == 0:
                if dotInPolygon(pluv.lat, pluv.lon, for_processing):
                    db.Pluviometer_Area.insert(id_area=area.id, id_pluviometer=pluv.id)
    db.commit()

# Method not used anymore
# @request.restful()
# def marker_dragg():
#     """Updates the marker location and it`s area in the database"""
#     response.view = 'generic.json'
#
#     def POST(*args, **kwargs):
#         pluv_id = request.vars.id
#         lat = request.vars.lat
#         lon = request.vars.lon
#
#         db(db.Pluviometer.id == pluv_id).update(lat=lat, lon=lon)
#
#         # This code will break when there are more areas for pluviometer
#         for area in db(db.Area.id > 0).select():
#             point_nodes = db(db.AreaNode.id_area == area.id).select()
#             nodes_array = []
#             for area_node in point_nodes:
#                 nodes_array.append([area_node.lat, area_node.lon])
#             if dotInPolygon(lat, lon, nodes_array):
#                 db(db.Pluviometer_Area.id_pluviometer == pluv_id).update(id_area=area.id)
#                 break
#
#         return dict()
#
#     return locals()