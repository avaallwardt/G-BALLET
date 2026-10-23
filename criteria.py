# Step 3: Criteria scores
# Based on the features, how well each technique criteria is satisfied
#
# Now i suppose we evaluate each of these technique criteria independently and generate an output if some are not met
# (output can depend on what the specific image has. For example, if the angle is significantly lower than needed, we output something specific…)
#
# Scores: "good", "moderate" (moderate issue), "major" (major issue), "na" (not scored)

from .feedback import FEEDBACK, NOT_ARABESQUE

T = {
    # Supporting knee
    "supporting_knee_straight": 177,     # at or above this, the knee reads as straight either way (stops tiny landmark noise from flipping the cross product sign)
    "hyperextension_limit": 170,         # if supporting_angle < 170: "Overhyperextended"
    "slightly_bent": 160,                # bent knee between this and 175 = "slightly bent", below = "Supporting knee bent."
    "working_knee_straight": 175,        # Metric 1 (first version): if working_angle > 175.0: straight
    "working_knee_major": 165,
    # Working leg height
    "height_goal": 90,                   # if height > 90
    "height_almost": 75,
    # Wing
    "wing_low": 165,                     # if 165 < wing_deg < 180
    "wing_major": 150,
    # Supporting leg turnout (raw normalized triangle area)
    "turnout_area": 0.0004,              # "We will say turned out supporting leg is 0.0004 and below, else is turned in"
    "turnout_area_major": 0.0009,        # "turned in max : triangle area: ~ 0.0009"
    # Working leg turnout (heel distance from ankle-toe line / foot length)
    "heel_offset": 0.10,
    "heel_offset_major": 0.20,
    # Hips (distance between hip landmarks / torso length)
    "hip_separation": 0.30,
    "hip_separation_major": 0.45,
    # Chest & Back
    "torso_lean": 45,                    # degrees forward from vertical
    "torso_lean_major": 60,
    "sternum_head": 15,                  # degrees from vertical either way
    "sternum_head_major": 25,
    "shoulder_separation": 0.25,
    "shoulder_separation_major": 0.45,
    # Head
    "gaze_min": 5,                       # degrees above level
    "gaze_max": 35,
    # Front arm
    "front_arm_min": 25,                 # lowered from 30-45 to 25-30
    "front_arm_max": 30,
    "front_arm_slack": 10,               # within 10 degrees of the range = moderate, further = major
    "wrist_max": 170,                    # around 150 degrees for break in wrist
    "wrist_min": 140,
    "elbow_max": 175,                    # slightly less than 180 degrees
    "elbow_min": 155,
    # Side arm
    "side_elbow": 165,                   # should be 180 degrees
    # Is it a 1st arabesque arm? (front arm angle must be in this window)
    "first_arabesque_arm_min": -15,
    "first_arabesque_arm_max": 60,
    # Visibility
    "min_visibility": 0.5,               # MediaPipe visibility below this = can't see it clearly
}


def check_arabesque(f):
    '''
    Is this an arabesque photo? Returns None if yes, otherwise the reason it isn't.
    '''
    if f["_vis"]["legs"] < T["min_visibility"] or not f["_legs_in_frame"]:
        return "legs_hidden"
    if not f["_supporting_ankle_below_hip"] or f["_supporting_leg_lean"] > 35:
        return "not_standing"
    if f["working_leg_height"] < 45:
        return "leg_not_lifted"
    if f["shoulder_separation"] > 0.8 and f["hip_separation"] > 0.5:
        return "front_view"
    if f["_nose_points_backward"]:
        return "leg_in_front"
    if f["working_knee_angle"] < 130:
        return "attitude"
    return None


def row(key, score, feedback, feature=None, note=None):
    return {"key": key, "score": score, "feedback": feedback, "feature": feature, "note": note}


def not_visible(key, feature=None):
    return row(key, "na", FEEDBACK["not_visible"], feature)


def score_criteria(f):
    '''
    Input: features dict from extract_features
    Output: dict of element -> list of scored constraints
    '''
    vis = f["_vis"]
    ok = lambda part: vis[part] >= T["min_visibility"]
    out = {}

    # ---------------- Supporting Leg ----------------
    rows = []

    # Rotated (sole of shoe at least partially showing)
    area = f["supporting_foot_area"]
    feat = f"supporting foot triangle area = {area:.5f}"
    if not ok("supporting_foot"):
        rows.append(not_visible("supporting_rotated", feat))
    elif area <= T["turnout_area"]:
        rows.append(row("supporting_rotated", "good", FEEDBACK["supporting_rotated.good"], feat, FEEDBACK["supporting_rotated.note"]))
    else:
        score = "major" if area > T["turnout_area_major"] else "moderate"
        rows.append(row("supporting_rotated", score, FEEDBACK["supporting_rotated.turned_in"], feat, FEEDBACK["supporting_rotated.note"]))

    # Knee straight
    # Hip-knee-angle close to 180 degrees, slightly past 180 degrees ok for hyperextension
    angle = f["supporting_knee_angle"]
    direction = "hyperextended" if f["supporting_knee_hyperextends"] else "bent"
    feat = f"supporting knee angle = {angle:.0f}° ({direction} side)"
    if angle >= T["supporting_knee_straight"]:
        rows.append(row("supporting_knee", "good", FEEDBACK["supporting_knee.straight"], feat))
    elif f["supporting_knee_hyperextends"]:
        if angle < T["hyperextension_limit"]:
            rows.append(row("supporting_knee", "moderate", FEEDBACK["supporting_knee.overhyperextended"], feat))
        else:
            rows.append(row("supporting_knee", "good", FEEDBACK["supporting_knee.good_hyperextension"], feat))
    elif angle >= T["working_knee_straight"]:
        rows.append(row("supporting_knee", "good", FEEDBACK["supporting_knee.straight"], feat))
    elif angle >= T["slightly_bent"]:
        rows.append(row("supporting_knee", "moderate", FEEDBACK["supporting_knee.slightly_bent"], feat))
    else:
        rows.append(row("supporting_knee", "major", FEEDBACK["supporting_knee.bent"], feat))
    out["supporting_leg"] = rows

    # ---------------- Working Leg ----------------
    rows = []

    # Metric 1: Working Leg Straight
    # Combines both versions of Metric 1: the cross product says which way the knee bends,
    # and the original > 175 rule keeps a nearly straight knee from counting as bent.
    angle = f["working_knee_angle"]
    feat = f"working knee angle = {angle:.0f}°"
    if f["working_knee_bends_wrong_way"] and angle < T["working_knee_straight"]:
        score = "major" if angle < T["working_knee_major"] else "moderate"
        rows.append(row("working_straight", score, FEEDBACK["working_straight.bent"], feat))
    else:
        rows.append(row("working_straight", "good", FEEDBACK["working_straight.straight"], feat))

    # Metric 2: Working Leg Height
    height = f["working_leg_height"]
    feat = f"working leg height = {height:.0f}°"
    if height > T["height_goal"]:
        rows.append(row("working_height", "good", FEEDBACK["working_height.high"].format(height=height), feat))
    elif height >= T["height_almost"]:
        rows.append(row("working_height", "moderate", FEEDBACK["working_height.almost"].format(height=height), feat))
    else:
        rows.append(row("working_height", "major", FEEDBACK["working_height.low"].format(height=height), feat))

    # Metric 3: Working Foot Wing
    wing = f["wing_deg"]
    feat = f"wing degree = {wing:.0f}°"
    if not ok("working_foot"):
        rows.append(not_visible("working_wing", feat))
    elif wing > T["wing_low"]:
        rows.append(row("working_wing", "good", FEEDBACK["working_wing.good"].format(wing=wing), feat))
    else:
        score = "major" if wing < T["wing_major"] else "moderate"
        rows.append(row("working_wing", score, FEEDBACK["working_wing.not_winged"].format(wing=wing), feat))

    # Metric 6: Working leg turnout
    offset = f["working_heel_offset"]
    feat = f"heel distance from ankle-toe line = {offset:.2f} foot lengths"
    if not ok("working_foot"):
        rows.append(not_visible("working_rotated", feat))
    elif offset <= T["heel_offset"]:
        rows.append(row("working_rotated", "good", FEEDBACK["working_rotated.good"], feat))
    else:
        score = "major" if offset > T["heel_offset_major"] else "moderate"
        rows.append(row("working_rotated", score, FEEDBACK["working_rotated.heel_showing"], feat, FEEDBACK["working_rotated.note"]))
    out["working_leg"] = rows

    # ---------------- Hips ----------------
    sep = f["hip_separation"]
    feat = f"hip separation = {sep:.2f} torso lengths"
    if sep <= T["hip_separation"]:
        out["hips"] = [row("hips_square", "good", FEEDBACK["hips_square.good"], feat)]
    else:
        score = "major" if sep > T["hip_separation_major"] else "moderate"
        out["hips"] = [row("hips_square", score, FEEDBACK["hips_square.open"], feat)]

    # ---------------- Chest & Back ----------------
    rows = []
    lean = f["torso_lean"]
    feat = f"torso lean = {lean:.0f}° from vertical"
    if lean <= T["torso_lean"]:
        rows.append(row("chest_lifted", "good", FEEDBACK["chest_lifted.good"], feat))
    else:
        score = "major" if lean > T["torso_lean_major"] else "moderate"
        rows.append(row("chest_lifted", score, FEEDBACK["chest_lifted.dropping"], feat))

    head_lean = f["sternum_head_lean"]
    side = "forward" if head_lean > 0 else "back"
    feat = f"sternum to head line = {abs(head_lean):.0f}° {side} of vertical"
    if not ok("head"):
        rows.append(not_visible("sternum_head", feat))
    elif abs(head_lean) <= T["sternum_head"]:
        rows.append(row("sternum_head", "good", FEEDBACK["sternum_head.good"], feat))
    else:
        score = "major" if abs(head_lean) > T["sternum_head_major"] else "moderate"
        rows.append(row("sternum_head", score, FEEDBACK[f"sternum_head.{side}"], feat))

    sep = f["shoulder_separation"]
    feat = f"shoulder separation = {sep:.2f} torso lengths"
    if sep <= T["shoulder_separation"]:
        rows.append(row("back_square", "good", FEEDBACK["back_square.good"], feat, FEEDBACK["back_square.note"]))
    else:
        score = "major" if sep > T["shoulder_separation_major"] else "moderate"
        rows.append(row("back_square", score, FEEDBACK["back_square.open"], feat, FEEDBACK["back_square.note"]))
    out["chest_back"] = rows

    # ---------------- Arms: is this 1st arabesque? ----------------
    first_arabesque = (ok("front_arm")
                       and T["first_arabesque_arm_min"] <= f["front_arm_angle"] <= T["first_arabesque_arm_max"])

    # ---------------- Head ----------------
    gaze = f["gaze_angle"]
    feat = f"gaze = {gaze:.0f}° above level"
    if first_arabesque:
        feat += f", finger = {f['finger_angle_from_head']:.0f}°"
    if not ok("head"):
        out["head"] = [not_visible("head_gaze", feat)]
    elif gaze < T["gaze_min"]:
        out["head"] = [row("head_gaze", "moderate", FEEDBACK["head_gaze.too_low"], feat)]
    elif gaze > T["gaze_max"]:
        out["head"] = [row("head_gaze", "moderate", FEEDBACK["head_gaze.too_high"], feat)]
    elif first_arabesque and gaze < f["finger_angle_from_head"] - 5:
        out["head"] = [row("head_gaze", "moderate", FEEDBACK["head_gaze.below_finger"], feat)]
    else:
        out["head"] = [row("head_gaze", "good", FEEDBACK["head_gaze.good"], feat)]

    # ---------------- Arm in Front of Body for 1st Arabesque ----------------
    if not first_arabesque:
        skipped = FEEDBACK["front_arm.not_first"]
        out["front_arm"] = [row(k, "na", skipped) for k in ("front_arm_angle", "front_wrist", "front_elbow")]
        out["front_arm"].append(row("front_fingers", "na", FEEDBACK["fingers.unsure"]))
        out["side_arm"] = [row(k, "na", skipped) for k in ("side_below", "side_straight")]
        out["side_arm"].append(row("side_fingers", "na", FEEDBACK["fingers.unsure"]))
        return out, first_arabesque

    rows = []
    angle = f["front_arm_angle"]
    feat = f"front arm angle = {angle:.0f}°"
    if T["front_arm_min"] <= angle <= T["front_arm_max"]:
        rows.append(row("front_arm_angle", "good", FEEDBACK["front_arm_angle.good"].format(angle=angle), feat))
    else:
        low = angle < T["front_arm_min"]
        off = (T["front_arm_min"] - angle) if low else (angle - T["front_arm_max"])
        score = "moderate" if off <= T["front_arm_slack"] else "major"
        rows.append(row("front_arm_angle", score, FEEDBACK["front_arm_angle." + ("low" if low else "high")].format(angle=angle), feat))

    wrist = f["front_wrist_angle"]
    feat = f"arm-wrist-fingers angle = {wrist:.0f}°"
    if T["wrist_min"] <= wrist <= T["wrist_max"]:
        rows.append(row("front_wrist", "good", FEEDBACK["front_wrist.good"], feat))
    elif wrist > T["wrist_max"]:
        rows.append(row("front_wrist", "moderate", FEEDBACK["front_wrist.straight"], feat))
    else:
        rows.append(row("front_wrist", "moderate", FEEDBACK["front_wrist.too_broken"], feat))

    elbow = f["front_elbow_angle"]
    feat = f"elbow angle = {elbow:.0f}°"
    if T["elbow_min"] <= elbow <= T["elbow_max"]:
        rows.append(row("front_elbow", "good", FEEDBACK["front_elbow.good"], feat))
    elif elbow > T["elbow_max"]:
        rows.append(row("front_elbow", "moderate", FEEDBACK["front_elbow.straight"], feat))
    else:
        rows.append(row("front_elbow", "moderate", FEEDBACK["front_elbow.too_bent"], feat))

    rows.append(row("front_fingers", "na", FEEDBACK["fingers.unsure"]))
    out["front_arm"] = rows

    # ---------------- Arm to Side of Body ----------------
    rows = []
    below = f["side_wrist_below_shoulder"]
    feat = f"wrist is {abs(below):.2f} torso lengths {'below' if below > 0 else 'above'} shoulder"
    if not ok("side_arm"):
        rows.append(not_visible("side_below", feat))
    elif below > 0:
        rows.append(row("side_below", "good", FEEDBACK["side_below.good"], feat))
    else:
        rows.append(row("side_below", "moderate", FEEDBACK["side_below.too_high"], feat))

    elbow = f["side_elbow_angle"]
    feat = f"shoulder-elbow-wrist angle = {elbow:.0f}°"
    if not ok("side_arm"):
        rows.append(not_visible("side_straight", feat))
    elif elbow >= T["side_elbow"]:
        rows.append(row("side_straight", "good", FEEDBACK["side_straight.good"], feat))
    else:
        rows.append(row("side_straight", "moderate", FEEDBACK["side_straight.bent"], feat))

    rows.append(row("side_fingers", "na", FEEDBACK["fingers.unsure"]))
    out["side_arm"] = rows

    return out, first_arabesque
