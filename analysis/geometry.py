# Geometry helpers
# These are the functions from balletanalysis.py, moved here so every metric can share them.
# Docstrings and comments are kept as you wrote them. Anything added is marked "(added)".

# Import math to have functions like sqrt
import math


# We can write a general `angle at` function that finds the angle between two vectors ba and bc
def angle_at(a, b, c):
    '''
    Input:
    a: NormalizedLandmark
    b: NormalizedLandmark
    c: NormalizedLandmark

    Output:
    Angle (in degrees) between vectors ba and bc
    '''
    ba = (a.x - b.x, a.y - b.y)
    bc = (c.x - b.x, c.y - b.y)
    mag_ba = math.hypot(ba[0], ba[1])
    mag_bc = math.hypot(bc[0], bc[1])
    dot = ba[0] * bc[0] + ba[1] * bc[1]
    cos = dot / (mag_ba * mag_bc)

    # (added) floating point error can push cos slightly past 1 or -1, which would crash acos
    cos = max(-1.0, min(1.0, cos))

    angle_radians = math.acos(cos) # arccos ensures we get the principal angle between the two vectors (btwn 0 and 180)
    angle_degrees = math.degrees(angle_radians)

    return angle_degrees


# Problem: I dont necessarily want principal angle. Which side the principal leg is on matters. Otherwise bent knee and straight knee are both "hyperextended"
    # arccos gives unsigned angle in [0, 180]
    # we don't know which way the knee bends toward
# Solution: For knee straightness, we need angle orientation
    # 2d cross product

def cross(a, b, c): # if swap a and c then cross product will have opposite sign
    """
    Input:
    a: NormalizedLandmark
    b: NormalizedLandmark
    c: NormalizedLandmark

    Output:
    2d cross product (aka magnitude of 3d cross product)
    """
    ba = (a.x - b.x, a.y - b.y)
    bc = (c.x - b.x, c.y - b.y)

    ba_cross_bc = ba[0] * bc[1] - ba[1] * bc[0]

    return ba_cross_bc


# Calculate triangle area from 3 coordinates
def triangle_area(a, b, c):
    '''
    Calculate the area of a triangle using the shoelace formula.

    Input:
    a: NormalizedLandmark
    b: NormalizedLandmark
    c: NormalizedLandmark

    Output:
    Area of the triangle formed by the three points (float)
    '''
    area = 0.5 * abs(a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y))

    return area


def dist(a, b):
    '''
    Find distance between 2 coordinates and b.
    Input:
    a: NormalizedLandmark
    b: NormalizedLandmark

    Output:
    distance (scalar), normalized by foot length
    '''
    dx = a.x - b.x
    dy = a.y - b.y
    return math.hypot(dx, dy)


def perp_dist(p, a, b):
    '''
    Find the perpendicular distance from the point p to the line described by points a and b.
    Input:
    p: NormalizedLandmark
    a: NormalizedLandmark
    c: NormalizedLandmark
    Output:
    distance (scalar)
    '''
    # direction vector of line ab
    a_b = (b.x - a.x, b.y - a.y)

    # perpendicular direction vector through p
    p_line = (-a_b[1], a_b[0])

    # (added) finished from here, following your steps
    # draw p_line
    # points on p_line are p + s * p_line, points on line ab are a + t * a_b

    # find intersection of new line with a-b line
    # the intersection is the projection of p onto line ab:
    # t = (ap dot ab) / (ab dot ab)
    a_p = (p.x - a.x, p.y - a.y)
    t = (a_p[0] * a_b[0] + a_p[1] * a_b[1]) / (a_b[0] ** 2 + a_b[1] ** 2)
    intersection = (a.x + t * a_b[0], a.y + t * a_b[1])

    # find distance from p to point of intersection
    return math.hypot(p.x - intersection[0], p.y - intersection[1])
