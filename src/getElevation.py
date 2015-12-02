#!/usr/bin/env python

# Author: Patricio Gonzalez Vivo - 2015 (@patriciogv)
# Thanks to Derek Watkins ( @dwtkns ) for collectiong the data 
# and making it easy to use in this project http://dwtkns.com/srtm30m/

import json
from common import getRange, getBoundingBox, degToMeters, tileForMeters, toMercator, remap, remapPoints

data_path = '../data'
ID = 'N37W123'
USGS_URL = "http://e4ftl01.cr.usgs.gov/SRTM/SRTMGL1.003/2000.02.11/"
USGS_BBOX_PATH = data_path+"/srtm30m_bounding_boxes.json"

with open(USGS_BBOX_PATH) as data_file:    
    data = json.load(data_file)

points = []
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


with open(data_path+'/'+ID+'.json', 'w') as outfile:
    outfile.write(json.dumps(geoJSON, outfile, indent=4))
outfile.close()


# gdal_translate -ot Int16 -of PNG N37W123.hgt outfile.png