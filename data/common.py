import requests, json, math
import numpy
import matplotlib
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
from PIL import Image

import shapely.geometry
import shapely.geometry.polygon 

def getVerticesFromTile(x,y,zoom):
    KEY = "vector-tiles-NumPyGZu-Q"
    r = requests.get(("http://vector.mapzen.com/osm/all/%i/%i/%i.json?api_key="+KEY) % (zoom,x,y))
    j = json.loads(r.text)
    p = [] # Array of points
    for layer in j:
        if layer == 'buildings' or layer == 'roads' or layer == 'water' or layer == 'landuse':
            for features in j[layer]:
                if features == 'features':
                    for feature in j[layer][features]:
                        if feature['geometry']['type'] == 'LineString':
                            p.extend(feature['geometry']['coordinates'])                                
                        elif feature['geometry']['type'] == 'Polygon':
                            for shapes in feature['geometry']['coordinates']:
                                p.extend(shapes)
                        elif feature['geometry']['type'] == 'MultiLineString':
                            for shapes in feature['geometry']['coordinates']:
                                p.extend(shapes)
                        elif feature['geometry']['type'] == 'MultiPolygon':
                            for polygon in feature['geometry']['coordinates']:
                                for shapes in polygon:
                                    p.extend(shapes)
                                    
    return p

def getHeights(coords):
    KEY = "elevation-6va6G1Q"
    JSON = {}
    JSON['shape'] = []
    for lon,lat in coords:
        point = {}
        point['lat'] = lat
        point['lon'] = lon
        JSON['shape'].append(point)
    J = json.dumps(JSON)
    R = requests.post('http://elevation.mapzen.com/height?api_key=%s' % KEY, data=J)
    return json.loads(R.text)['height']

def getRange(array):
    min = 1000000
    max = -1000000
    for element in array:
        if element < min:
            min = element
        if element > max:
            max = element
    return [min,max]

def getBoundingBox(P):
    min_x = min_y = 9999999999.0
    max_x = max_y = -9999999999.0
    for x,y in P:
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y
    return [min_x, max_x, min_y, max_y]

# Convert lat-lng to mercator meters
half_circumference_meters = 20037508.342789244;
def latLngToMeters(coord):
    y = float(coord[1]) # Lon
    x = float(coord[0]) # Lat
    # Latitude
    y = math.log(math.tan(y*math.pi/360 + math.pi/4)) / math.pi
    y *= half_circumference_meters

    # Longitude
    x *= half_circumference_meters/180;
    return [x,y]

def toMercator(coords):
    points = []
    for coord in coords:
        points.append(latLngToMeters(coord))
    return points

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

def remap(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def makeHeighmap(name,size, bbox, height_range, points, heights):
    total_samples = len(points)
    if total_samples != len(heights):
        print("Length don't match")
        return

    width = bbox[1]-bbox[0]
    height = bbox[3]-bbox[2]
    aspect = width/height
    
    image = Image.new("RGB", (int(size), int(size*aspect)))
    putpixel = image.putpixel
    imgx, imgy = image.size
    nx = []
    ny = []
    nr = []
    ng = []
    nb = []
    for i in range(total_samples):
        nx.append(remap(points[i][0],bbox[0],bbox[1],0,imgx))
        ny.append(remap(points[i][1],bbox[2],bbox[3],imgy,0))
        bri = int(remap(heights[i],height_range[0],height_range[1],0,255))
        nr.append(bri)
        ng.append(bri)
        nb.append(bri)
    for y in range(imgy):
        for x in range(imgx):
            dmin = math.hypot(imgx-1, imgy-1)
            j = -1
            for i in range(total_samples):
                d = math.hypot(nx[i]-x, ny[i]-y)
                if d < dmin:
                    dmin = d
                    j = i
            putpixel((x, y), (nr[j], ng[j], nb[j]))
    image.save(name+".png", "PNG")
    image.show()

def makeGeometry(triangle):
    poly = []
    for vertex in triangle:
        poly.append(tuple(vertex))

    geom = shapely.geometry.Polygon(poly)
    cw_geom = shapely.geometry.polygon.orient(geom, sign=-1)
    # return shapely.geometry.mapping(cw_geom)
    poly = []
    for vertex in cw_geom.exterior.coords:
        x, y = vertex
        poly.append([x, y])
    return poly

def makeGeoJson(name,triangles):
    geoJSON = {}
    geoJSON['type'] = "FeatureCollection";
    geoJSON['features'] = [];

    element = {}
    element['type'] = "Feature"
    element['geometry'] = {}
    element['geometry']['type'] = "Polygon"
    element['geometry']['coordinates'] = []
    element['properties'] = {}
    element['properties']['kind'] = "terrain"

    for tri in triangles:
        if len(tri) == 3:
            element['geometry']['coordinates'].append(makeGeometry(tri));
    
    geoJSON['features'].append(element);

    with open(name+'.json', 'w') as outfile:
        outfile.write(json.dumps(geoJSON, outfile, indent=4))
    outfile.close()

