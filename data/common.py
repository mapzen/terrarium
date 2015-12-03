import math

def getStringRangeToArray(data):
    array = []
    if isinstance(data, basestring):
        for part in data.split(','):
            if '-' in part:
                a, b = part.split('-')
                a, b = int(a), int(b)
                array.extend(range(a, b + 1))
            else:
                a = int(part)
                array.append(a)
    elif isinstance(data, list):
        array = data
    else:
        array = [int(data)]
    return array

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
    for point in P:
        if point[0] < min_x:
            min_x = point[0]
        if point[0] > max_x:
            max_x = point[0]
        if point[1] < min_y:
            min_y = point[1]
        if point[1] > max_y:
            max_y = point[1]
    return [min_x, max_x, min_y, max_y]

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
