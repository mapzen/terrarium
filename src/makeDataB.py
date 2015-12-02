#!/usr/bin/env python

# Author: Patricio Gonzalez Vivo - 2015 (@patriciogv)
from tools import makeTile, makeTiles

DATA_PATH = '../data/B'
OSM_ID = "111968" #sys.argv[1]
ZOOMS = "3-17" #sys.argv[2]

makeTiles(DATA_PATH, OSM_ID, ZOOMS)
# makeTile(655,1582,12)
