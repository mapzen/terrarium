#!/usr/bin/env python

# Author: Patricio Gonzalez Vivo - 2015 (@patriciogv)
# Thanks to Derek Watkins ( @dwtkns ) for collectiong the data 
# and making it easy to use in this project http://dwtkns.com/srtm30m/

import json
from common import getStringRangeToArray, getBoundingBox
from tile import toMercator
from terrarium import getPointsOfID, makeTilesOfPoints

DATA_PATH = '../data/A'
ID = 'N37W123' #sys.argv[1]
ZOOMS = "3-17" #sys.argv[2]
USGS_URL = "http://e4ftl01.cr.usgs.gov/SRTM/SRTMGL1.003/2000.02.11/"
USGS_BBOX_PATH = DATA_PATH+"/srtm30m_bounding_boxes.json"

with open(USGS_BBOX_PATH) as data_file:    
    data = json.load(data_file)

for layer in data['features']:
    if (layer['properties']['dataFile'].startswith(ID) ):
        points_latlon = layer['geometry']['coordinates'][0]
        points_merc = toMercator(points_latlon);

bbox_merc = getBoundingBox(points_merc);
print(bbox_merc)

geoJSON = {}
geoJSON['type'] = "FeatureCollection";
geoJSON['features'] = [];

element = {}
element['type'] = "Feature"
element['geometry'] = {}
element['geometry']['type'] = "Polygon"
element['geometry']['coordinates'] = []
element['properties'] = {}
element['properties']['kind'] = "water"

element['geometry']['coordinates'].append(points_latlon)

geoJSON['features'].append(element);

with open(DATA_PATH+'/'+ID+'.json', 'w') as outfile:
    outfile.write(json.dumps(geoJSON, outfile, indent=4))
outfile.close()

zoom_array = getStringRangeToArray(ZOOMS)

## MAKE TILES for all zoom levels
##

points = points_latlon;
# points = getPointsOfID("111968")

for zoom in zoom_array:
    makeTilesOfPoints(DATA_PATH, points, zoom, False)
