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

# TODO
#	- download tile and bounding box JSON
# "wget " + USGS_URL + ID + ".SRTMGL1.hgt.zip"
# "wget http://dwtkns.com/srtm30m/srtm30m_bounding_boxes.json"
# 	- unzip tile
# "tar xzvf "+ ID +".SRTMGL1.hgt.zip"
# 	- convert it to PNG
# "gdal_translate -ot Int16 -of PNG " + ID ".hgt " + ID + ".png"

with open(USGS_BBOX_PATH) as data_file:    
    data = json.load(data_file)

for layer in data['features']:
    if (layer['properties']['dataFile'].startswith(ID) ):
        points_latlon = layer['geometry']['coordinates'][0]
        points_merc = toMercator(points_latlon);

bbox_merc = getBoundingBox(points_merc);
print(bbox_merc)

# Make big square tile with the size of the heighmap image for the water
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

# Fetch all the tiles on the ZOOMS range
zoom_array = getStringRangeToArray(ZOOMS)
points = points_latlon;

for zoom in zoom_array:
    makeTilesOfPoints(DATA_PATH, points, zoom, False)
