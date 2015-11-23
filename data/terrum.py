#!/usr/bin/env python

# Author: Patricio Gonzalez Vivo - 2015 (@patriciogv)
from common import getVerticesFromTile, toMercator, getHeights, getBoundingBox, getRange, getTriangles, showTriangles, makeHeighmap, makeGeoJson

# tile = [1309,3166,13]
# tile = [19293,24640,16]
tile = [655,1582,12]
name = str(tile[0])+'-'+str(tile[1])+'-'+str(tile[2])

# Vertices
points_latlon = getVerticesFromTile(tile[0],tile[1],tile[2])
points_merc = toMercator(points_latlon)

# Elevation
heights = getHeights(points_latlon)
heights_range = getRange(heights)

triangles = getTriangles(points_latlon)
makeGeoJson(name, triangles)

bbox_latlon = getBoundingBox(points_latlon)
showTriangles(triangles, bbox_latlon)
# print("Ranges", bbox_latlon, heights_range)
# print("Coord", bbox_latlon[0], bbox_latlon[2])
# print("Width", bbox_latlon[1]-bbox_latlon[0], bbox_latlon[3]-bbox_latlon[2])
# makeHeighmap(name, 500, bbox_latlon, heights_range, points_latlon, heights)

bbox_merc = getBoundingBox(points_merc)
print("Ranges", bbox_merc, heights_range)
print("Coord", bbox_merc[0], bbox_merc[2])
print("Width", bbox_merc[1]-bbox_merc[0], bbox_merc[3]-bbox_merc[2])
makeHeighmap(name, 500, bbox_merc, heights_range, points_merc, heights)
