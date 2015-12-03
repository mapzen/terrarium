#!/usr/bin/env python

# Author: Patricio Gonzalez Vivo - 2015 (@patriciogv)
from terrarium import getPointsOfID, makeTile, makeTilesOfPoints
form common import getStringRangeToArray

DATA_PATH = '../data/B'
OSM_ID = "111968" #sys.argv[1]
ZOOMS = "3-17" #sys.argv[2]

# makeTile(655,1582,12)

points = getPointsOfID(OSM_ID)
zoom_array = getStringRangeToArray(ZOOMS)

for zoom in zoom_array:
    makeTilesOfPoints(path, points, zoom, True)