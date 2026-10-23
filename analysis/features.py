# Step 2: extract interpretable features from landmarks

# Features = values you compute from the landmarks
# They represent the measurable properties that body parts give rise to
# Interpretable features = when humans can understand what the features mean
    # E.g. this feature measures knee straightness, therefore the feature is an interprtable feature

import math

from .geometry import angle_at, cross, triangle_area, dist, perp_dist
from .landmarks import NOSE, LEFT_EAR, RIGHT_EAR, LEFT, RIGHT, Point


def midpoint(a, b):
    return Point((a.x + b.x) / 2, (a.y + b.y) / 2, min(a.visibility, b.visibility))


def lean_from_vertical(bottom, top, facing):
    '''
    (added) Angle (degrees) of the line bottom -> top away from straight up.
    Positive = leaning toward the direction the dancer faces, negative = leaning back.
    Y-coordinate increases downward, so "up" is negative y.
    '''
    return math.degrees(math.atan2((top.x - bottom.x) * facing, bottom.y - top.y))


def elevation(start, end, facing):
    '''
    (added) Angle (degrees) of the line start -> end above horizontal, measured toward the
    direction the dancer faces. 0 = level, positive = upward, negative = downward.
    '''
    return math.degrees(math.atan2(start.y - end.y, (end.x - start.x) * facing))


def extract_features(raw, points):
    '''
    Input:
    raw:    MediaPipe NormalizedLandmarks (used where your thresholds were calibrated on raw normalized coordinates)
    points: the same landmarks with x and y in the same units (used for every angle)

    Output:
    dict of interpretable features
    '''
    f = {}

    # Metric 1: Working Leg Straight

    # Determine which leg is working leg
    # Y-coordinate increases downward
    # So the ankle with the smaller y-coordinate is higher in the image and therefore is the working leg
    # However, this calculation assumes the image has proper orientation
    if raw[LEFT["ankle"]].y < raw[RIGHT["ankle"]].y:
        working_leg = "left"
    else:
        working_leg = "right"

    supporting_leg = "right" if working_leg == "left" else "left"
    W = LEFT if working_leg == "left" else RIGHT     # working side landmark indices
    S = RIGHT if working_leg == "left" else LEFT     # supporting side landmark indices
    f["working_leg"] = working_leg
    f["supporting_leg"] = supporting_leg

    p = points
    hip_mid = midpoint(p[23], p[24])
    shoulder_mid = midpoint(p[11], p[12])   # stands in for the sternum (MediaPipe has no sternum landmark)
    head_center = midpoint(p[LEFT_EAR], p[RIGHT_EAR])

    # (added) Which way is the dancer facing?
    # In an arabesque the working leg extends behind the body, so the dancer faces away from the working foot.
    # facing = +1 means facing image-right, -1 means facing image-left.
    # Your cross product rules were written as "working leg is left -> cross should be negative", which matched
    # your photos because MediaPipe labelled the working leg "left" whenever the dancer faced image-left.
    # Writing the rule in terms of facing direction gives the same answer on those photos, and still works
    # if MediaPipe swaps left/right (which it sometimes does on side views).
    facing = -1 if p[W["ankle"]].x > hip_mid.x else 1
    f["facing"] = "image-right" if facing == 1 else "image-left"
    f["_facing_sign"] = facing

    # Compute the knee angle (determine how bent the knee is)
    # Need 2 vectors: knee-hip and knee-ankle
    # Compute angle bewteen them
    # cos(theta) = u dot v / |u||v|
    f["working_knee_angle"] = angle_at(p[W["hip"]], p[W["knee"]], p[W["ankle"]])
    working_cross = cross(p[W["hip"]], p[W["knee"]], p[W["ankle"]])
    # working leg is left (facing image-left):
    # cross negative ==> hyperextension
    # cross positive ==> bent knee
    f["working_knee_bends_wrong_way"] = working_cross * facing < 0

    # Metric 2: Working Leg Height
    # Goal: want height above 90 degrees
    # Look at angle between hip - supporting ankle and hip - working ankle
    f["working_leg_height"] = angle_at(p[S["ankle"]], p[W["hip"]], p[W["ankle"]])

    # Metric 3: Working Foot Wing
    f["wing_deg"] = angle_at(p[W["knee"]], p[W["ankle"]], p[W["foot"]])

    # Metric 4: Supporting Leg Straight
    # Cross product sign that corresponds to hyperextension vs bent knee depends on whether supporting leg is left or right
    # working leg is left (facing image-left): want principal angle to open to left, cross product should be negative
    f["supporting_knee_angle"] = angle_at(p[S["hip"]], p[S["knee"]], p[S["ankle"]])
    supporting_cross = cross(p[S["hip"]], p[S["knee"]], p[S["ankle"]])
    f["supporting_knee_hyperextends"] = supporting_cross * facing > 0

    # Metric 5: Supporting leg turnout
    # With more turnout, the heel moves behind the ankle from 2D perspective, so the ankle-heel-toe triangle collapses
    # (uses raw normalized coordinates, because that's what your 0.0004 threshold was measured in)
    f["supporting_foot_area"] = triangle_area(raw[S["ankle"]], raw[S["heel"]], raw[S["foot"]])

    # Metric 6: Working leg turnout
    # More rotation --> more of heel hidden behind ankle
    # V3: perpendicular distance from heel to ankle-toe line (normalized by foot length so photo size doesn't matter)
    foot_length = dist(p[W["ankle"]], p[W["foot"]])
    f["working_heel_offset"] = perp_dist(p[W["heel"]], p[W["ankle"]], p[W["foot"]]) / foot_length

    # Hips: square, should not be opening hip of working leg
    # (added) torso length = distance from hip midpoint to shoulder midpoint; used to make distances size-independent
    torso_length = dist(hip_mid, shoulder_mid)
    f["hip_separation"] = dist(p[23], p[24]) / torso_length
    # hip_tilt = difference between left hip height and right hip height (working hip above supporting hip is positive)
    f["hip_tilt"] = (p[S["hip"]].y - p[W["hip"]].y) / torso_length

    # Chest & Back
    # Sternum to center of head should be vertical line relative to rest of arabesque
    f["sternum_head_lean"] = lean_from_vertical(shoulder_mid, head_center, facing)
    # Lifted and supported: how far the torso tips forward from vertical
    f["torso_lean"] = lean_from_vertical(hip_mid, shoulder_mid, facing)
    # also need to make sure back is square - based on distance between right shoulder and left shoulder
    f["shoulder_separation"] = dist(p[11], p[12]) / torso_length

    # Head: looking slightly upward over the finger
    # (added) gaze = direction from center of head (between the ears) to the nose
    f["gaze_angle"] = elevation(head_center, p[NOSE], facing)

    # Arms
    # (added) the arm in front of the body is the one whose wrist reaches furthest in the direction the dancer faces
    if p[LEFT["wrist"]].x * facing > p[RIGHT["wrist"]].x * facing:
        F, A = LEFT, RIGHT
    else:
        F, A = RIGHT, LEFT
    f["front_arm"] = "left" if F is LEFT else "right"

    # front_arm_angle = angle from shoulder to wrist (top of hand -> index finger landmark)
    f["front_arm_angle"] = elevation(p[F["shoulder"]], p[F["index"]], facing)
    f["front_elbow_angle"] = angle_at(p[F["shoulder"]], p[F["elbow"]], p[F["wrist"]])
    f["front_wrist_angle"] = angle_at(p[F["elbow"]], p[F["wrist"]], p[F["index"]])
    f["finger_angle_from_head"] = elevation(head_center, p[F["index"]], facing)
    f["finger_in_front_of_face"] = (p[F["index"]].x - p[NOSE].x) * facing > 0

    # Arm to side: below shoulder, shoulder-elbow-wrist 180 degrees
    # (positive = wrist is below the shoulder, in torso lengths)
    f["side_wrist_below_shoulder"] = (p[A["wrist"]].y - p[A["shoulder"]].y) / torso_length
    f["side_elbow_angle"] = angle_at(p[A["shoulder"]], p[A["elbow"]], p[A["wrist"]])

    # (added) the raw numbers behind each feature, so the website can show the geometry
    f["_idx"] = {"W": W, "S": S, "F": F, "A": A}
    f["_raw"] = {
        "working_cross": working_cross,
        "supporting_cross": supporting_cross,
        "heel_perp": perp_dist(p[W["heel"]], p[W["ankle"]], p[W["foot"]]),
        "foot_length": foot_length,
        "torso_length": torso_length,
        "hip_dist": dist(p[23], p[24]),
        "shoulder_dist": dist(p[11], p[12]),
    }

    # (added) how confident MediaPipe is about the landmarks each criterion uses
    vis = lambda *idx: min(p[i].visibility for i in idx)
    f["_vis"] = {
        "legs": vis(23, 24, 25, 26, 27, 28),
        "supporting_foot": vis(S["ankle"], S["heel"], S["foot"]),
        "working_foot": vis(W["ankle"], W["heel"], W["foot"]),
        "head": vis(NOSE, LEFT_EAR, RIGHT_EAR),
        "front_arm": vis(F["shoulder"], F["elbow"], F["wrist"], F["index"]),
        "side_arm": vis(A["shoulder"], A["elbow"], A["wrist"]),
    }
    # (added) a few extra measurements used only by the "is this an arabesque?" check
    # MediaPipe still guesses landmarks that are cut off, so check the legs are actually inside the photo
    f["_legs_in_frame"] = all(-0.02 <= raw[i].x <= 1.02 and -0.02 <= raw[i].y <= 1.02 for i in range(23, 33))
    f["_supporting_leg_lean"] = abs(lean_from_vertical(p[S["ankle"]], p[S["hip"]], facing))
    f["_supporting_ankle_below_hip"] = p[S["ankle"]].y > hip_mid.y
    ear_to_nose = (p[NOSE].x - head_center.x) * facing
    f["_nose_points_backward"] = ear_to_nose < -0.5 * dist(head_center, p[NOSE])

    return f
