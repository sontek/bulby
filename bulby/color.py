import struct
import math
import codecs
from collections import namedtuple


XYPoint = namedtuple('XYPoint', ['x', 'y'])
Red = XYPoint(0.675, 0.322)
Lime = XYPoint(0.4091, 0.518)
Blue = XYPoint(0.167, 0.04)


def cross_product(p1, p2):
    ''' Returns the cross product of two ``XYPoints``.'''
    return (p1.x * p2.y - p1.y * p2.x)


def in_lamp_reach(p):
    ''' Check if the provided XYPoint can be recreated by a Hue lamp. '''
    v1 = XYPoint(Lime.x - Red.x, Lime.y - Red.y)
    v2 = XYPoint(Blue.x - Red.x, Blue.y - Red.y)

    q = XYPoint(p.x - Red.x, p.y - Red.y)
    s = cross_product(q, v2) / cross_product(v1, v2)
    t = cross_product(v1, q) / cross_product(v1, v2)

    return (s >= 0.0) and (t >= 0.0) and (s + t <= 1.0)


def get_closest_point_to_line(A, B, P):
    '''
    Find the closest point on a line. This point will be reproducible by a Hue
    lamp.
    '''
    AP = XYPoint(P.x - A.x, P.y - A.y)
    AB = XYPoint(B.x - A.x, B.y - A.y)
    ab2 = AB.x * AB.x + AB.y * AB.y
    ap_ab = AP.x * AB.x + AP.y * AB.y
    t = ap_ab / ab2

    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0

    return XYPoint(A.x + AB.x * t, A.y + AB.y * t)


def get_distance_between_two_points(one, two):
    '''
    Returns the distance between two ``XYPoint`` objects.
    '''
    dx = one.x - two.x
    dy = one.y - two.y
    return math.sqrt(dx * dx + dy * dy)


def get_closest_point_to_point(xy_point):
    '''
    Used to find the closest point to an unreproducible Color is unreproducible
    on each line in the CIE 1931 'triangle'.
    '''
    pAB = get_closest_point_to_line(Red, Lime, xy_point)
    pAC = get_closest_point_to_line(Blue, Red, xy_point)
    pBC = get_closest_point_to_line(Lime, Blue, xy_point)

    # Get the distances per point and see which point is closer to our Point.
    dAB = get_distance_between_two_points(xy_point, pAB)
    dAC = get_distance_between_two_points(xy_point, pAC)
    dBC = get_distance_between_two_points(xy_point, pBC)

    lowest = dAB
    closest_point = pAB

    if (dAC < lowest):
        lowest = dAC
        closest_point = pAC

    if (dBC < lowest):
        lowest = dBC
        closest_point = pBC

    # Change the xy value to a value which is within the reach of the lamp.
    cx = closest_point.x
    cy = closest_point.y

    return XYPoint(cx, cy)


def get_xy_from_hex(hex_value):
    '''
    Returns X, Y coordinates containing the closest avilable CIE 1931
    based on the hex_value provided.
    '''
    red, green, blue = struct.unpack('BBB', codecs.decode(hex_value, 'hex'))
    r = ((red + 0.055) / (1.0 + 0.055)) ** 2.4 if (red > 0.04045) else (red / 12.92)  # pragma: noqa
    g = ((green + 0.055) / (1.0 + 0.055)) ** 2.4 if (green > 0.04045) else (green / 12.92)  # pragma: noqa
    b = ((blue + 0.055) / (1.0 + 0.055)) ** 2.4 if (blue > 0.04045) else (blue / 12.92)  # pragma: noqa

    X = r * 0.4360747 + g * 0.3850649 + b * 0.0930804
    Y = r * 0.2225045 + g * 0.7168786 + b * 0.0406169
    Z = r * 0.0139322 + g * 0.0971045 + b * 0.7141733

    if X + Y + Z == 0:
        cx = cy = 0
    else:
        cx = X / (X + Y + Z)
        cy = Y / (X + Y + Z)

    # Check if the given XY value is within the colourreach of our lamps.
    xy_point = XYPoint(cx, cy)
    is_in_reach = in_lamp_reach(xy_point)

    if not is_in_reach:
        xy_point = get_closest_point_to_point(xy_point)

    return xy_point
