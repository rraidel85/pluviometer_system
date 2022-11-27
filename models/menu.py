# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

def controller(name):
    return request.controller == name

def function(name):
    return request.function == name

# response.menu["title", active menu, url, "icon", [submenu]]
response.menu = [
    (T('Inicio'), controller("default") and function("index"), URL('default', 'index'), 'ti-dashboard', []),
    (T('Mapa'), controller("map") and function("mapa"), URL('map', 'mapa'), 'ti-map-alt', []),
    (T('Pluviómetros'), controller("pluviometer") and function("index"), '#', 'ti-location-pin', [
        (T('Listado'), controller("pluviometer") and function("pluv_list"), URL('pluviometer', 'pluv_list')),
        (T('Crear en el mapa'), controller("pluviometer") and function("index"), URL('pluviometer', 'create_pluv')),
        (T('Editar en el mapa'), controller("pluviometer") and function("index"), URL('pluviometer', 'edit_pluv')),
    ]),
    (T('Áreas'), controller("area") and function("area_list"), '#', 'ti-direction', [
        (T('Listado'), controller("area") and function("area_list"), URL('area', 'area_list')),
        (T('Crear en el mapa'), controller("area") and function("create_area"), URL('area', 'create_area')),
        (T('Editar en el mapa'), controller("area") and function("edit_area"), URL('area', 'edit_area')),
    ]),
    (T('Precipitaciones'), controller("registers") and function("registers_list"), URL('registers', 'registers_list'), 'ti-map-alt', []),
    (T('Tipos de área'), controller("area_type") and function("areatype_list"), URL('area_type', 'areatype_list'), 'ti-map-alt', []),
    (T('Tipos de pluviómetro'), controller("pluv_type") and function("pluvtype_list"), URL('pluv_type', 'pluvtype_list'), 'ti-map-alt', []),
    (T('Calcular'), controller("math") and function("select_math"), URL('math', 'select_math'), 'ti-stats-down', []),
    (T('Graficos'), controller("graphics"), '#', 'fa fa-area-chart', [
        (T('Ind Conc Pluv'), controller("graphics") and function("select_graphic"), URL('graphics', 'select_graphic')),
    ]),
    (T('Usuarios'), controller("user") and function("user_list"), URL('user', 'user_list'),
     'ti-map-alt', []),

]

page_type = {
    'pluv': URL('graphics','c_index_pluviometer_graphic'),
    'area': URL('graphics','c_index_area_graphic'),
}


@cache('areas', None, cache.ram)
def __getAreaNodes():
    """
    Get all area nodes for all areas
    The format of the output will be:
    areas = {
        "Municipios" : [{
            "BARAGUA": [id_area, [area_borders]],
            "MORON": [id_area, [area_borders], id_area_type],
            },
            color,
            description],
        "Cuencas" : [{
            "Cuenca Río Chambas": [id_area, [area_borders], id_area_type],
            },
            color,
            description],
        }
    """
    areas = {}

    for area_type in db(db.AreaType.id > 0).select():
        area_borders = {}
        for area in db().select(db.Area.id, db.Area.id_area_type, db.Area.name, db.Area.sub_name):
            if area.id_area_type == area_type.id:
                key = area.sub_name if area.sub_name else area.name
                area_borders[key] = [area.id, [], area_type.id]
                for area_node in db(db.AreaNode.id_area == area.id).select(db.AreaNode.lat, db.AreaNode.lon):
                    area_borders[key][1].append([area_node.lat, area_node.lon])
        areas[area_type.name] = [area_borders, area_type.representation, area_type.description]

    return areas