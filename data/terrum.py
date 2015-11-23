#!/usr/bin/env python

# Author: Patricio Gonzalez Vivo - 2015 (@patriciogv)
from common import getPointsFromTile, getHeights, getBoundingBox, getRange, getTriangles, showTriangles, makeHeighmap, makeGeoJson

# tile = [1309,3166,13]
tile = [19293,24640,16]

name = str(tile[0])+'-'+str(tile[1])+'-'+str(tile[2])

P = getPointsFromTile(tile[0],tile[1],tile[2])
H = getHeights(P)

height_range = getRange(H)
bbox = getBoundingBox(P)
print(bbox,height_range)

triangles = getTriangles(P)
makeGeoJson(name,triangles)

# showTriangles(triangles,bbox)
# makeHeighmap(name,500, bbox, height_range, P, H)
