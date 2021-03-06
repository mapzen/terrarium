#!/usr/bin/env python

# Authors: 
# 	- Patricio Gonzalez Vivo (@patriciogv)
#	- Kevin Kreiser (@kevinkreiser)
#
import sys
from terrarium import getPointsOfID, makeTile, makeTilesOfPoints
from common import getStringRangeToArray

DATA_PATH = '../data/B'
OSM_ID = "111968" 
ZOOMS = "3-20"

if (len(sys.argv) > 1):
	OSM_ID = sys.argv[1]
if (len(sys.argv) > 2):
	ZOOMS = sys.argv[2]
if (len(sys.argv) > 3):
	DATA_PATH = sys.argv[3]

# makeTile(DATA_getTileBoundingBoxATH, 655, 1582, 12, True)
# makeTile(DATA_PATH, 1310, 3166, 13, True)

points = getPointsOfID(OSM_ID)
zoom_array = getStringRangeToArray(ZOOMS)

for zoom in zoom_array:
    makeTilesOfPoints(DATA_PATH, points, zoom, True)