#!/usr/bin/env python

# Author: Patricio Gonzalez Vivo -height_range 2015 (@patriciogv)
from terrarium import getPointsOfID, makeTile, makeTilesOfPoints
from common import getStringRangeToArray

# TODO:
# 	- Use arguments

DATA_PATH = '../data/B'
OSM_ID = "111968" #sys.argv[1]
ZOOMS = "3-17" #sys.argv[2]

makeTile(DATA_PATH, 655, 1582, 12, True)
# makeTile(DATA_PATH, 1310, 3166, 13, True)

# points = getPointsOfID(OSM_ID)
# zoom_array = getStringRangeToArray(ZOOMS)

# for zoom in zoom_array:
#     makeTilesOfPoints(DATA_PATH, points, zoom, True)