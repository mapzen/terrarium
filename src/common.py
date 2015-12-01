import math

half_circumference_meters = 20037508.342789244;

def getRange(array):
    min = 1000000
    max = -1000000
    for element in array:
        if element < min:
            min = element
        if element > max:
            max = element
    return [min,max]

def getBoundingBox(P):
    min_x = min_y = 9999999999.0
    max_x = max_y = -9999999999.0
    for x,y in P:
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y
    return [min_x, max_x, min_y, max_y]

# Convert lat-lng to mercator meters
def latLngToMeters(coord):
    y = float(coord[1]) # Lon
    x = float(coord[0]) # Lat
    # Latitude
    y = math.log(math.tan(y*math.pi/360 + math.pi/4)) / math.pi
    y *= half_circumference_meters

    # Longitude
    x *= half_circumference_meters/180;
    return [x,y]

# Convert lat-lng to mercator meters
def degToMeters( coords ):
    y = float(coords['y'])
    x = float(coords['x'])
    # Latitude
    y = math.log(math.tan(y*math.pi/360 + math.pi/4)) / math.pi
    y *= half_circumference_meters

    # Longitude
    x *= half_circumference_meters / 180;

    return {"x": x, "y": y}

# Given a point in mercator meters and a zoom level, return the tile X/Y/Z that the point lies in
def tileForMeters(coords, zoom):
    y = float(coords['y'])
    x = float(coords['x'])
    return {
        "x": math.floor((x + half_circumference_meters) / (half_circumference_meters * 2 / pow(2, zoom))),
        "y": math.floor((-y + half_circumference_meters) / (half_circumference_meters * 2 / pow(2, zoom))),
        "z": zoom
    }

def toMercator(coords):
    points = []
    for coord in coords:
        points.append(latLngToMeters(coord))
    return points

def remap(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    if (leftSpan != 0): 
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)
    else:
        return rightMin

# [min_in_x, max_in_x, min_in_y, max_in_y], [min_out_x, max_out_x, min_out_y, max_out_y]
def remapPoints(P, in_bbox, out_bbox ):
    points = []
    for p in P:
        points.append([remap(p[0], in_bbox[0], in_bbox[1], out_bbox[0], out_bbox[1]), remap(p[1], in_bbox[2], in_bbox[3], out_bbox[2], out_bbox[3])])
    return points
