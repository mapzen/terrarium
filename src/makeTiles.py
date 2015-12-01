#!/usr/bin/env python

# Author: Patricio Gonzalez Vivo - 2015 (@patriciogv)
import sys
from tools import makeTile, makeTiles

osm_id = "111968" #sys.argv[1]
zooms = "3-17" #sys.argv[2]

makeTiles(osm_id, zooms)
# makeTile(655,1582,12)
