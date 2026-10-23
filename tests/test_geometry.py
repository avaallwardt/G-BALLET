# Checks for the geometry helpers in analysis/geometry.py
#   python3 -m pytest

import math

from analysis.geometry import angle_at, cross, triangle_area, dist, perp_dist
from analysis.landmarks import Point


def P(x, y):
    return Point(x, y)


def test_angle_at_right_angle():
    assert math.isclose(angle_at(P(1, 0), P(0, 0), P(0, 1)), 90)


def test_angle_at_straight_line():
    assert math.isclose(angle_at(P(0, 0), P(0, 1), P(0, 2)), 180)


def test_angle_at_handles_rounding_past_180():
    # nearly collinear points can push cos slightly past -1
    assert angle_at(P(0, 0), P(1e-9, 1), P(0, 2)) <= 180


def test_cross_sign_flips_when_a_and_c_swap():
    a, b, c = P(0, 0), P(0.1, 1), P(0, 2)
    assert cross(a, b, c) == -cross(c, b, a)
    assert cross(a, b, c) != 0


def test_triangle_area():
    assert math.isclose(triangle_area(P(0, 0), P(2, 0), P(0, 2)), 2)


def test_triangle_area_collinear_is_zero():
    assert triangle_area(P(0, 0), P(1, 1), P(2, 2)) == 0


def test_dist():
    assert math.isclose(dist(P(0, 0), P(3, 4)), 5)


def test_perp_dist():
    # distance from (1, 3) to the x-axis is 3
    assert math.isclose(perp_dist(P(1, 3), P(0, 0), P(5, 0)), 3)
