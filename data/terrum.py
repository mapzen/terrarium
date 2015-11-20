#!/usr/bin/env python

# Author: Patricio Gonzalez Vivo - 2015 (@patriciogv)
from common import getPointsFromTile, getHeights, getBoundingBox, getTriangles, showTriangles

P = getPointsFromTile(19293,24640,16)
height = getHeights(P)

bbox = getBoundingBox(P)

triangles = getTriangles(P)
showTriangles(triangles,bbox)
