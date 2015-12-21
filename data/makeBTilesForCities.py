#!/usr/bin/env python

# Authors: 
#   - Patricio Gonzalez Vivo (@patriciogv)
#   - Kevin Kreiser (@kevinkreiser)
#
import sys, os
from terrarium import getPointsOfID, makeTile, makeTilesOfPoints
from common import getStringRangeToArray

CITIES = "cities.txt" 
ZOOMS = "3-18"
DATA_PATH = '../data/B'

if (len(sys.argv) > 1):
    CITIES = sys.argv[1]
if (len(sys.argv) > 2):
    ZOOMS = sys.argv[2]
if (len(sys.argv) > 3):
    DATA_PATH = sys.argv[3]

zoom_array = getStringRangeToArray(ZOOMS)

with open(CITIES, "r") as lines:
    for line in lines:
        city = line.split(',')
        OSM_ID = city[1].rstrip('\r\n').strip()

        print "Start coocking tiles for city " + city[0]
        points = getPointsOfID(OSM_ID)
        
        for zoom in zoom_array:
            makeTilesOfPoints(DATA_PATH, points, zoom, True)