# Tile operations tools
# some of them taken from https://github.com/mapzen/tilequeue/blob/master/tilequeue/tile.py

# from TileStache.Geography import SphericalMercator
from common import getBoundingBox
import math

half_circumference_meters = 20037508.342789244;

# http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

# http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int(
        (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi)
        / 2.0 * n)
    return (xtile, ytile)

def getTileBoundingBox(x, y, zoom):
    topleft_lat, topleft_lng = num2deg(x, y, zoom)
    bottomright_lat, bottomright_lng = num2deg(
        x + 1, y + 1, zoom)
    min_x = topleft_lng
    min_y = bottomright_lat
    max_x = bottomright_lng
    max_y = topleft_lat

    # tile_to_bounds is used to calculate boxes that could be off the grid
    # clamp the max values in that scenario
    max_x = min(180, max_x)
    max_y = min(90, max_y)

    return [min_x, max_x, min_y, max_y]

def getTileMercatorBoundingBox(x, y, zoom):
    bbox = getTileBoundingBox(x, y, zoom)
    min = latLngToMeters([bbox[0],bbox[2]])
    max = latLngToMeters([bbox[1],bbox[3]])
    return [min[1], min[0], max[1], max[0]]

# Convert lat-lng to mercator meters
def latLngToMeters(point):
    y = float(point[1]) # Lon
    x = float(point[0]) # Lat
    # Latitude
    y = math.log(math.tan(y*math.pi/360 + math.pi/4)) / math.pi
    y *= half_circumference_meters

    # Longitude
    x *= half_circumference_meters/180;
    return [x, y]

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