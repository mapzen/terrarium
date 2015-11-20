import requests, json
import numpy
import matplotlib
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

def getPointsFromTile(x,y,zoom):
    KEY = "vector-tiles-NumPyGZu-Q"
    r = requests.get(("http://vector.mapzen.com/osm/all/%i/%i/%i.json?api_key="+KEY) % (zoom,x,y))
    j = json.loads(r.text)
    p = [] # Array of points
    for layer in j:
        if layer == 'buildings' or layer == 'roads' or layer == 'water' or layer == 'landuse':
            for features in j[layer]:
                if features == 'features':
                    for feature in j[layer][features]:
                        for coords in feature['geometry']['coordinates']:
                            if not type(coords) is float:
                                if type(coords[0]) is float:
                                    p.append(coords)
                                else:
                                    p.extend(coords)
    return p

def getHeights(points):
    KEY = "elevation-6va6G1Q"
    JSON = {}
    JSON['shape'] = []
    for lon,lat in points:
        point = {}
        point['lat'] = lat
        point['lon'] = lon
        JSON['shape'].append(point)
    J = json.dumps(JSON,separators=(',',':'))
    R = requests.get(('http://elevation.mapzen.com/height?json=%s&api_key='+KEY) %(J))
    print(R)
    # print(json.loads(R.text))

def getBoundingBox(points):
    min_x = min_y = 180.0
    max_x = max_y = -180.0
    for x,y in points:
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y
    return [min_x, max_x, min_y, max_y]

def getTriangles(P):
    delauny = Delaunay(P)
    triangles = delauny.points[delauny.vertices]
    return triangles

def showTriangles(triangles,bbox):
    fig = plt.figure(figsize=(4.5,4.5))
    axes = plt.subplot(1,1,1)

    # Triangle vertices
    A = triangles[:, 0]
    B = triangles[:, 1]
    C = triangles[:, 2]
    lines = []
    lines.extend(zip(A, B))
    lines.extend(zip(B, C))
    lines.extend(zip(C, A))
    lines = matplotlib.collections.LineCollection(lines, color='r')
    plt.gca().add_collection(lines)
    plt.axis(bbox)
    plt.show()
