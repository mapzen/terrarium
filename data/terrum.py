#!/usr/bin/env python

# Author: Patricio Gonzalez Vivo - 2015 (@patriciogv)
import requests, json
import numpy
import matplotlib
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

def getBoundingBox(points):
    min_x = 180
    min_y = 180
    max_x = -180
    max_y = -180
    for point in points:
        print(point)
        if min_x < point[0]:
            min_x = point[0]
        if max_x > point[0]:
            max_x = point[0]
        if min_y < point[1]:
            min_y = point[1]
        if max_y > point[1]:
            max_y = point[1]

    return [min_x, max_x, min_y, max_y]

def getPointsFromTile(x,y,zoom):
    r = requests.get("http://vector.mapzen.com/osm/all/%i/%i/%i.json?api_key=vector-tiles-NumPyGZu-Q" % (zoom,x,y))
    j = json.loads(r.text)
    p = [] # Array of points
    for layer in j:
        if layer == 'buildings' or layer == 'roads' or layer == 'water':
            for features in j[layer]:
                if features == 'features':
                    for feature in j[layer][features]:
                        for coords in feature['geometry']['coordinates']:
                            if not type(coords) is float:
                                if type(coords[0]) is float:
                                    p.append(coords)
                                else:
                                    p.extend(coords)
    return p

def voronoi(P):
    delauny = Delaunay(P)
    triangles = delauny.points[delauny.vertices]
    
    lines = []

    # Triangle vertices
    A = triangles[:, 0]
    B = triangles[:, 1]
    C = triangles[:, 2]
    lines.extend(zip(A, B))
    lines.extend(zip(B, C))
    lines.extend(zip(C, A))
    lines = matplotlib.collections.LineCollection(lines, color='r')
    plt.gca().add_collection(lines)

    circum_centers = numpy.array([triangle_csc(tri) for tri in triangles])

    segments = []
    for i, triangle in enumerate(triangles):
        circum_center = circum_centers[i]
        for j, neighbor in enumerate(delauny.neighbors[i]):
            if neighbor != -1:
                segments.append((circum_center, circum_centers[neighbor]))
            else:
                ps = triangle[(j+1)%3] - triangle[(j-1)%3]
                ps = numpy.array((ps[1], -ps[0]))

                middle = (triangle[(j+1)%3] + triangle[(j-1)%3]) * 0.5
                di = middle - triangle[j]

                ps /= numpy.linalg.norm(ps)
                di /= numpy.linalg.norm(di)

                if numpy.dot(di, ps) < 0.0:
                    ps *= -1000.0
                else:
                    ps *= 1000.0
                segments.append((circum_center, circum_center + ps))
    return segments

def triangle_csc(pts):
    rows, cols = pts.shape

    A = numpy.bmat([[2 * numpy.dot(pts, pts.T), numpy.ones((rows, 1))],
                 [numpy.ones((1, rows)), numpy.zeros((1, 1))]])

    b = numpy.hstack((numpy.sum(pts * pts, axis=1), numpy.ones((1))))
    x = numpy.linalg.solve(A,b)
    bary_coords = x[:-1]
    return numpy.sum(pts * numpy.tile(bary_coords.reshape((pts.shape[0], 1)), (1, pts.shape[1])), axis=0)

P = getPointsFromTile(19293,24640,16)
bbox = getBoundingBox(P)
print(bbox)
fig = plt.figure(figsize=(4.5,4.5))
axes = plt.subplot(1,1,1)

segments = voronoi(P)
lines = matplotlib.collections.LineCollection(segments, color='k')
axes.add_collection(lines)
plt.axis(bbox)
plt.show()
