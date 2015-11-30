#!/usr/bin/env python

# Author: Patricio Gonzalez Vivo - 2015 (@patriciogv)
import requests, sys
import xml.etree.ElementTree as ET
from common import makeTile, makeTiles

OSMID="111968" #sys.argv[1]
ZOOM=[12,13,14,15,16,17]

# if isinstance(sys.argv[2], basestring):
#     for part in sys.argv[2].split(','):
#         if '-' in part:
#             a, b = part.split('-')
#             a, b = int(a), int(b)
#             ZOOM.extend(range(a, b + 1))
#         else:
#             a = int(part)
#             ZOOM.append(a)
# else:
#     ZOOM=[int(sys.argv[2])]

# if len(sys.argv) < 3:
#     print "At least 2 arguments needed - please enter an OSM ID and zoom level."
#     sys.exit()

success = False
try:
    INFILE = 'http://www.openstreetmap.org/api/0.6/relation/'+OSMID+'/full'
    print "Downloading", INFILE
    r = requests.get(INFILE)
    r.raise_for_status()
    success = True
except Exception, e:
    print e

if not success:
    try:
        INFILE = 'http://www.openstreetmap.org/api/0.6/way/'+OSMID+'/full'
        print "Downloading", INFILE
        r = requests.get(INFILE)
        r.raise_for_status()
        success = True
    except Exception, e:
        print e

if not success:
    try:
        INFILE = 'http://www.openstreetmap.org/api/0.6/node/'+OSMID
        print "Downloading", INFILE
        r = requests.get(INFILE)
        r.raise_for_status()
        success = True
    except Exception, e:
        print e
        print "Element not found, exiting"
        sys.exit()

# print r.encoding
open('outfile.xml', 'w').close() # clear existing OUTFILE

with open('outfile.xml', 'w') as fd:
  fd.write(r.text.encode("UTF-8"))
  fd.close()

try:
    tree = ET.parse('outfile.xml')
except Exception, e:
    print e
    print "XML parse failed, please check outfile.xml"
    sys.exit()

root = tree.getroot()

print "Processing:"

points = []
for node in root:
    if node.tag == "node":
        lat = float(node.attrib["lat"])
        lon = float(node.attrib["lon"])
        points.append({'y':lat, 'x':lon})

##
## GET TILES for all zoom levels
##
for z in ZOOM:
    makeTiles(points,z)

# makeTile(655,1582,12)
