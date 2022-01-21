def dotInPolygon(x, y, polygon):
    """Comprueba si un punto se encuentra dentro de un polígono

           poligono - Lista de tuplas con los puntos que forman los vértices [(x1, x2), (x2, y2), ..., (xn, yn)]
        """
    i = 0
    j = len(polygon) - 1
    to_return = False
    for i in range(len(polygon)):
        if (polygon[i][1] < y <= polygon[j][1]) or (polygon[j][1] < y <= polygon[i][1]):
            if polygon[i][0] + (y - polygon[i][1]) / (polygon[j][1] - polygon[i][1]) * (
                    polygon[j][0] - polygon[i][0]) < x:
                to_return = not to_return
        j = i
    return to_return