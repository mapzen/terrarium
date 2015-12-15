# Tile operations tools
# some of them taken from https://github.com/mapzen/tilequeue/blob/master/tilequeue/tile.py

# from TileStache.Geography import SphericalMercator
from common import getBoundingBox
import math

half_circumference_meters = 20037508.342789244;

# Convert lat-lng to mercator meters
def latLngToMeters(point):
    y = float(point[1]) # Lon
    x = float(point[0]) # Lat
    # Latitude
    y = math.log(math.tan(y*math.pi/360 + math.pi/4)) / math.pi
    y *= half_circumference_meters

    # Longitude
    x *= half_circumference_meters/180;
    return [x,y]

# Given a point in mercator meters and a zoom level, return the tile X/Y/Z that the point lies in
def tileForMeters(points, zoom):
    return [int(math.floor((float(points[0]) + half_circumference_meters) / (half_circumference_meters * 2 / pow(2, zoom)))),
            int(math.floor((-float(points[1]) + half_circumference_meters) / (half_circumference_meters * 2 / pow(2, zoom)))),
            zoom]

def toMercator(P):
    points = []
    for point in P:
        points.append(latLngToMeters(point))
    return points

# Inclusive Range
rangeIn = lambda start, end: range(start, end+1)

# Return an array of tiles that contain a set of points
def getTilesForPoints(points, zoom):
    bbox = getBoundingBox(points)

    print bbox

    A = tileForMeters(latLngToMeters([bbox[0],bbox[2]]), zoom)
    B = tileForMeters(latLngToMeters([bbox[1],bbox[3]]), zoom)

    if (A[0] == B[0]):
        rows = [A[0]]
    else:
        mn = min(A[0],B[0])
        mx = max(A[0],B[0])
        rows = rangeIn(mn,mx)

    if (A[1] == B[1]):
        cols = [A[1]]
    else:
        mn = min(A[1],B[1])
        mx = max(A[1],B[1])
        cols = rangeIn(mn,mx)

    tiles = []
    for row in rows:
        for col in cols:
            tiles.append({'x':row,'y':col, 'z':zoom})
    return tiles