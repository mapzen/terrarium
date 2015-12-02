#!/usr/bin/env python

# Author: Patricio Gonzalez Vivo - 2015 (@patriciogv)
from tools import makeTile, makeTiles

data_path = '../data/B'
osm_id = "111968" #sys.argv[1]
zooms = "3-17" #sys.argv[2]

makeTiles(data_path, osm_id, zooms, true)
# makeTile(655,1582,12)
