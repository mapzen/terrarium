# Author: Patricio Gonzalez Vivo - 2015 (@patriciogv)

import requests, json, math, os, sys
import numpy
from scipy.spatial import Delaunay
from PIL import Image
import xml.etree.ElementTree as ET
import shapely.geometry
import shapely.geometry.polygon 

from common import getStringRangeToArray, getRange, getBoundingBox, remap, remapPoints
from tile import getTilesForPoints, toMercator

ELEVATION_RASTER_TILE_SIZE = 256

# Given a tile coordinate get the points using Mapzen's Vector Tiles service
def getPointsFromTile(x, y, zoom, layers):
    KEY = "vector-tiles-NPGZu-Q"
    r = requests.get(("http://vector.mapzen.com/osm/all/%i/%i/%i.json?api_key="+KEY) % (zoom,x,y))
    j = json.loads(r.text)
    p = [] # Array of points
    for layer in j:
        if layer in layers:
            for features in j[layer]:
                if features == 'features':
                    for feature in j[layer][features]:
                        if feature['geometry']['type'] == 'LineString':
                            p.extend(feature['geometry']['coordinates'])                                
                        elif feature['geometry']['type'] == 'Polygon':
                            for shapes in feature['geometry']['coordinates']:
                                #  TODO:
                                #       - drop the extra vertex
                                p.extend(shapes)
                        elif feature['geometry']['type'] == 'MultiLineString':
                            for shapes in feature['geometry']['coordinates']:
                                p.extend(shapes)
                        elif feature['geometry']['type'] == 'MultiPolygon':
                            for polygon in feature['geometry']['coordinates']:
                                for shapes in polygon:
                                    #  TODO:
                                    #       - drop the extra vertex
                                    p.extend(shapes)
                                    
    return p

def getPointsAndGroupsFromTile(x, y, zoom, layers):
    KEY = "vector-tiles-NPGZu-Q"
    r = requests.get(("http://vector.mapzen.com/osm/all/%i/%i/%i.json?api_key="+KEY) % (zoom,x,y))
    j = json.loads(r.text)
    p = [] # Array of points
    g = [] # Group of vertices with forced height (buildings)
    for layer in j:
        if layer in layers:
            for features in j[layer]:
                if features == 'features':
                    for feature in j[layer][features]:
                        if feature['geometry']['type'] == 'LineString':
                            p.extend(feature['geometry']['coordinates'])                                
                        elif feature['geometry']['type'] == 'Polygon':
                            for shapes in feature['geometry']['coordinates']:
                                #  TODO:
                                #       - drop the extra vertex
                                if layer == 'buildings':
                                    g.append([len(p),len(shapes)])
                                p.extend(shapes)
                        elif feature['geometry']['type'] == 'MultiLineString':
                            for shapes in feature['geometry']['coordinates']:
                                p.extend(shapes)
                        elif feature['geometry']['type'] == 'MultiPolygon':
                            for polygon in feature['geometry']['coordinates']:
                                #  TODO:
                                #       - drop the extra vertex
                                for shapes in polygon:
                                    if layer == 'buildings':
                                        g.append([len(p),len(shapes)])
                                    p.extend(shapes)
    return p, g

# Given set of points (in spherical mercator) fetch their elevation using Mapzen's Elevation Service
def getElevationFromPoints(points_merc):
    KEY = "elevation-6va6G1Q"

    # Transform the array of points to something the elevation service can read
    JSON = {}
    JSON['shape'] = []
    for lon,lat in points_merc:
        point = {}
        point['lat'] = lat
        point['lon'] = lon
        JSON['shape'].append(point)
    J = json.dumps(JSON)

    # Make a request and give back the answer (array of points)
    R = requests.post('http://elevation.mapzen.com/height?api_key=%s' % KEY, data=J)
    H = json.loads(R.text)['height']
    if (H):
        return H
    else:
        print("Response from elevation service, have no height",R.text)
        return []

# Given an array of points (array) tesselate them into triangles
def getTrianglesFromPoints(P):
    # Because of pressition issues spherical mercator points need to be normalize
    # in a bigger range. For that calculate the bounding box and map the points
    # into a normalize range
    bbox = getBoundingBox(P);
    normal = [-10000,10000,-10000,10000]
    points = remapPoints(P, bbox, normal)

    # Perform a Delaunay tessellation
    if len(points) < 3:
        print("Not enought points... no triangles")
        return []
    delauny = Delaunay(points)
    normalize_tri = delauny.points[delauny.vertices]

    # Un-normalize the points by remaping them to the original range
    triangles = []
    for triangle in normalize_tri:
        if len(triangle) == 3:
            triangles.append(remapPoints(triangle, normal, bbox));

    return triangles

# Given a set of points and height of the same lenght compose a voronoi PNG image
def makeHeighmap(path, name, size, height_range, points, heights):
    bbox = getBoundingBox(points)
    total_samples = len(points)
    if total_samples != len(heights):
        print("Length don't match")
        return
    
    image = Image.new("RGB", (int(size), int(size)))
    putpixel = image.putpixel
    imgx, imgy = image.size
    nx = []
    ny = []
    nr = []
    ng = []
    nb = []

    # Make samples data
    for i in range(total_samples):
        nx.append(remap(points[i][0], bbox[0], bbox[1], 0, imgx))
        ny.append(remap(points[i][1], bbox[2], bbox[3], imgy, 0))
        # TODO:
        #   - Don't use range maping. Encode a bigger range using RGB channels (rainbow pattern)
        bri = int(remap(heights[i],height_range[0],height_range[1],0,255))
        nr.append(bri)
        ng.append(bri)
        nb.append(bri)

    # Compute Voronoi (one-to-all)
    # TODO:
    #   - Improve this... is very expensive 
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

    image.save(path+'/'+name+".png", "PNG")

# Given a set of points return a valid 
def getPolygonFromPoints(points):
    # Shapely points are tuples, make an array of tuples
    poly = []
    for point in points:
        poly.append(tuple(point))

    # Points must have CW winding order
    geom = shapely.geometry.Polygon(poly)
    cw_geom = shapely.geometry.polygon.orient(geom, sign=-1)

    # TODO:
    #   - Use Shapely to return valid poligos or better a multipoligon

    # From tuples array to array of arrays
    poly = []
    for vertex in cw_geom.exterior.coords:
        x, y = vertex
        poly.append([x, y])

    return poly

# Given a set of triangles make a multi-polygon GeoJSON
def makeGeoJsonFromTriangles(path, name, triangles, height_range):
    geoJSON = {}
    geoJSON['type'] = "FeatureCollection";
    geoJSON['features'] = [];

    element = {}
    element['type'] = "Feature"
    element['geometry'] = {}
    element['geometry']['type'] = "MultiPolygon"
    element['geometry']['coordinates'] = []
    element['properties'] = {}
    element['properties']['kind'] = "terrain"
    if (len(height_range) > 1):
        element['properties']['min_height'] = height_range[0]
        element['properties']['max_height'] = height_range[1]

    for tri in triangles:
        # if len(tri) == 3:
        element['geometry']['coordinates'].append([getPolygonFromPoints(tri)]);
    
    geoJSON['features'].append(element);

    with open(path+'/'+name+'.json', 'w') as outfile:
        outfile.write(json.dumps(geoJSON, outfile, indent=4))
    outfile.close()

# make a GeoJSON (for the geometry) and/or a PNG IMAGE (for the elevation information) for the tile X,Y,Z
def makeTile(path, lng, lat, zoom, doPNGs):
    tile = [int(lng), int(lat), int(zoom)]

    print(" Zoom " + str(zoom) + " tile ", tile)
    name = str(tile[2])+'-'+str(tile[0])+'-'+str(tile[1])

    if os.path.isfile(path+'/'+name+".json"):
        print("Tile already created... skiping")
        return

    # Vertices
    layers = ['roads', 'water', 'landuse']
    if doPNGs:
        layers.append('buildings');
        print layers
        points_latlon, group = getPointsAndGroupsFromTile(tile[0], tile[1], tile[2], layers)
    else:
        points_latlon = getPointsFromTile(tile[0], tile[1], tile[2], layers)
    points_merc = toMercator(points_latlon)

    # Elevation
    heights = []
    heights_range = []
    if doPNGs:
        if os.path.isfile(path+'/'+name+".png"):
            print("Tile already created... skiping")
            return
        heights = getElevationFromPoints(points_latlon)
        heights_range = getRange(heights)

    # Tessellate points
    triangles = getTrianglesFromPoints(points_latlon)
    
    makeGeoJsonFromTriangles(path, name, triangles, heights_range)

    # Make Heighmap
    if doPNGs:
        makeHeighmap(path, name, ELEVATION_RASTER_TILE_SIZE, heights_range, points_merc, heights)

# Return all the points of a given OSM ID
def getPointsOfID (osmID):
    success = False
    try:
        INFILE = 'http://www.openstreetmap.org/api/0.6/relation/'+osmID+'/full'
        print "Downloading", INFILE
        r = requests.get(INFILE)
        r.raise_for_status()
        success = True
    except Exception, e:
        print e

    if not success:
        try:
            INFILE = 'http://www.openstreetmap.org/api/0.6/way/'+osmID+'/full'
            print "Downloading", INFILE
            r = requests.get(INFILE)
            r.raise_for_status()
            success = True
        except Exception, e:
            print e

    if not success:
        try:
            INFILE = 'http://www.openstreetmap.org/api/0.6/node/'+osmID
            print "Downloading", INFILE
            r = requests.get(INFILE)
            r.raise_for_status()
            success = True
        except Exception, e:
            print e
            print "Element not found, exiting"
            sys.exit()

    # print r.encoding
    open('outfile.xml', 'w').close() # clear existing OUTFILE

    with open('outfile.xml', 'w') as fd:
      fd.write(r.text.encode("UTF-8"))
      fd.close()

    try:
        tree = ET.parse('outfile.xml')
    except Exception, e:
        print e
        print "XML parse failed, please check outfile.xml"
        sys.exit()

    root = tree.getroot()

    print "Processing:"

    points = []
    for node in root:
        if node.tag == "node":
            points.append([float(node.attrib["lat"]),float(node.attrib["lon"])])
    return points

# Make all the tiles for points
def makeTilesOfPoints(path, points, zoom, doPNGs):
    tiles = getTilesForPoints(points, zoom)

    ## download tiles
    print "\Makeing %i tiles at zoom level %i" % (len(tiles), zoom)

    ## make/empty the tiles folder
    if not os.path.exists(path):
        os.makedirs(path)

    total = len(tiles)
    if total == 0:
        print("Error: no tiles")
        exit()
    count = 0
    sys.stdout.write("\r%d%%" % (float(count)/float(total)*100.))
    sys.stdout.flush()
    for tile in tiles:
        makeTile(path, tile['x'], tile['y'], tile['z'], doPNGs)
        count += 1
        sys.stdout.write("\r%d%%" % (float(count)/float(total)*100.))
        sys.stdout.flush()
