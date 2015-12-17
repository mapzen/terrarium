# Authors: @patriciogv, @kevinkreiser & @meetar

import requests, json, math, os, sys
import numpy
import cv2
from scipy.spatial import Delaunay
from PIL import Image
import xml.etree.ElementTree as ET
import shapely.geometry
import shapely.geometry.polygon 

from common import getStringRangeToArray, getRange, getBoundingBox, remap, remapPoints, isInBoundingBox
from tile import getTilesForPoints, toMercator, getTileBoundingBox, getTileMercatorBoundingBox

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
                                #  drop the extra vertex
                                shapes.pop()
                                p.extend(shapes)
                        elif feature['geometry']['type'] == 'MultiLineString':
                            for shapes in feature['geometry']['coordinates']:
                                p.extend(shapes)
                        elif feature['geometry']['type'] == 'MultiPolygon':
                            for polygon in feature['geometry']['coordinates']:
                                for shapes in polygon:
                                    #  Drop the extra vertex
                                    shapes.pop()
                                    p.extend(shapes)
                                    
    return p

def getPointsAndGroupsFromTile(x, y, zoom, layers):
    KEY = "vector-tiles-NPGZu-Q"
    bbox = getTileBoundingBox(x, y, zoom)

    r = requests.get(("http://vector.mapzen.com/osm/all/%i/%i/%i.json?api_key="+KEY) % (zoom,x,y))
    j = json.loads(r.text)
    P = [] # Array of points
    G = [] # Group of vertices with forced height (buildings)

    for layer in j:
        if layer in layers:
            for features in j[layer]:
                if features == 'features':
                    for feature in j[layer][features]:
                        if feature['geometry']['type'] == 'LineString':
                            P.extend(feature['geometry']['coordinates'])                                
                        elif feature['geometry']['type'] == 'Polygon':
                            for shapes in feature['geometry']['coordinates']:
                                #  drop the extra vertex
                                shapes.pop()
                                if layer == 'buildings':
                                    points = []
                                    for point in shapes:
                                        if isInBoundingBox(point, bbox):
                                            points.append(point)
                                    if (len(points) > 0):
                                        G.append([len(P),len(points)])
                                        P.extend(points)
                                else:
                                    P.extend(shapes)
                        elif feature['geometry']['type'] == 'MultiLineString':
                            for shapes in feature['geometry']['coordinates']:
                                P.extend(shapes)
                        elif feature['geometry']['type'] == 'MultiPolygon':
                            for polygon in feature['geometry']['coordinates']:
                                for shapes in polygon:
                                    #  drop the extra vertex
                                    shapes.pop()
                                    if layer == 'buildings':
                                        points = []
                                        for point in shapes:
                                            if isInBoundingBox(point, bbox):
                                                points.append(point)
                                        if (len(points) > 0):
                                            G.append([len(P),len(points)])
                                            P.extend(points)
                                    else:
                                        P.extend(shapes)
    return P, G

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
def getTrianglesFromPoints(P, tile):
    # Because of pressition issues spherical mercator points need to be normalize
    # in a bigger range. For that calculate the bounding box and map the points
    # into a normalize range
    bbox = getTileBoundingBox(tile[0], tile[1], tile[2])
    normal = [-10000,10000,-10000,10000]
    points = remapPoints(P, bbox, normal)

    # Perform a Delaunay tessellation
    delauny = Delaunay(points)
    normalize_tri = delauny.points[delauny.vertices]

    # Un-normalize the points by remaping them to the original range
    triangles = []
    for triangle in normalize_tri:
        if len(triangle) == 3:
            triangles.append(remapPoints(triangle, normal, bbox));

    return triangles

# Given a set of points and height of the same lenght compose a voronoi PNG image
def makeHeighmap(path, name, size, points, heights, tile):
    # bail if it doesnt look right
    total_samples = len(points)
    if total_samples != len(heights):
        print("Lengths don't match")
        return

    # convert mercator to pixels and map pixels to height values
    # bbox = getTileMercatorBoundingBox(tile[0], tile[1], tile[2])
    bbox = getBoundingBox(points)

    point_heights = {}
    for i in range(total_samples):
        x = int(remap(points[i][0], bbox[0], bbox[1], 0, size - 1))
        y = int(remap(points[i][1], bbox[2], bbox[3], size - 1, 0))
        point_heights[(x, y)] = heights[i]

    # subdivision from opencv, can do voronoi and its dual the delaunay triangulation
    subdiv = cv2.Subdiv2D((0, 0, size, size))
    for p in point_heights.iterkeys():
        subdiv.insert(p)
    (facets, centers) = subdiv.getVoronoiFacetList([])

    # an image where we will rasterize the voronoi cells
    image = numpy.zeros((size, size, 3), dtype = 'uint8')
    for i in xrange(0, len(facets)):
        ifacet_arr = []
        for f in facets[i]:
            ifacet_arr.append(f)
        ifacet = numpy.array(ifacet_arr, numpy.int)
        # the color is the height at the voronoi cite for this cell, offset to bring to unsigned 16bits
        height = point_heights[(centers[i][0], centers[i][1])] + 32768
        # to back them into a standard texture we split the high and low order bytes, note the order is G B R
        color = (int(math.floor(height % 255)), int(math.floor(height / 255) % 255), 0)
        # we exploit the fact that voronoi cells are convex polygons for faster rasterization
        cv2.fillConvexPoly(image, ifacet, color, cv2.CV_AA, 0)

    # we'll keep the result here
    cv2.imwrite(path + '/' + name + '.png', image)

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
def makeGeoJsonFromTriangles(path, name, triangles):
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

    for tri in triangles:
        # if len(tri) == 3:
        element['geometry']['coordinates'].append([getPolygonFromPoints(tri)]);
    
    geoJSON['features'].append(element);

    with open(path+'/'+name+'.json', 'w') as outfile:
        outfile.write(json.dumps(geoJSON, outfile, indent=4))
    outfile.close()

def getEquilizedHeightByGroup(heights, groups):
    for group in groups:
        start = group[0]
        end = start+group[1]
        mn = min(heights[start:end])
        for i in range(start,end):
            heights[i] = mn
    return heights

# make a GeoJSON (for the geometry) and/or a PNG IMAGE (for the elevation information) for the tile X,Y,Z
def makeTile(path, lng, lat, zoom, doPNGs):
    tile = [int(lng), int(lat), int(zoom)]

    name = str(tile[2])+'-'+str(tile[0])+'-'+str(tile[1])

    if os.path.isfile(path+'/'+name+".json"):
        if doPNGs:
            if os.path.isfile(path+'/'+name+".png"):
                print(" Tile already created... skiping")
                return
        else:
            print(" Tile already created... skiping")
            return

    # Vertices
    layers = ['roads', 'earth', 'water', 'landuse']  # We should add countours here
    groups = []
    if doPNGs:
        layers.append('buildings');
        points_latlon, groups = getPointsAndGroupsFromTile(tile[0], tile[1], tile[2], layers)
    else:
        points_latlon = getPointsFromTile(tile[0], tile[1], tile[2], layers)
    points_merc = toMercator(points_latlon)

    # Tessellate points
    if ( len(points_latlon) < 3 ):
        print(" Not enought points on tile... nothing to do")
        return

    triangles = getTrianglesFromPoints(points_latlon, tile)
    makeGeoJsonFromTriangles(path, name, triangles)

    # Elevation
    heights = []
    if doPNGs:
        if os.path.isfile(path+'/'+name+".png"):
            print("Tile already created... skiping")
            return
        heights = getElevationFromPoints(points_latlon)
        heights = getEquilizedHeightByGroup(heights, groups)
        heights_range = getRange(heights)
        makeHeighmap(path, name, ELEVATION_RASTER_TILE_SIZE, points_merc, heights, tile)

# Return all the points of a given OSM ID
# From Peter's https://github.com/tangrams/landgrab
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
            points.append([float(node.attrib["lon"]),float(node.attrib["lat"])])
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
        sys.stdout.write("\r%d%% " % (float(count)/float(total)*100.) + " tile " + str(tile) + ": ")
        sys.stdout.flush()
