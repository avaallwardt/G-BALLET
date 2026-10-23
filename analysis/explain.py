# Show the geometry behind each criterion.
#
# For every constraint this returns:
#   math:   the measurement in plain language, e.g. ["Knee angle (hip–knee–ankle)", "176.0°"]
#   shapes: what to draw on the photo (the website draws the angle, line, or triangle that was measured)
#
# Points in shapes are lists of MediaPipe landmark indices; a list with two indices means "the midpoint of these two".

HIP_MID = [23, 24]
SHOULDER_MID = [11, 12]   # sternum
HEAD_CENTER = [7, 8]      # center of head, between the ears


def deg(x):
    return f"{x:.1f}°"


def explain(key, f, T):
    """
    Returns {"shapes": [...], "math": [[label, value], ...]}.
    "math" is written in plain language for the dancer (no code), using the exact computed values.
    """
    W, S, F, A = (f["_idx"][k] for k in ("W", "S", "F", "A"))
    r = f["_raw"]
    facing = f["_facing_sign"]
    pt = lambda i: [i]

    if key == "supporting_rotated":
        return {
            "shapes": [{"type": "triangle", "points": [pt(S["ankle"]), pt(S["heel"]), pt(S["foot"])]}],
            "math": [
                ["Ankle–heel–toe triangle area", f"{f['supporting_foot_area']:.5f}"],
                ["Target", f"{T['turnout_area']} or less (smaller = more turned out)"],
            ],
        }

    if key == "supporting_knee":
        if f["supporting_knee_angle"] >= T["supporting_knee_straight"]:
            bend = "straight"
        else:
            bend = "backward (hyperextension)" if f["supporting_knee_hyperextends"] else "forward (bent)"
        return {
            "shapes": [{"type": "angle", "points": [pt(S["hip"]), pt(S["knee"]), pt(S["ankle"])],
                        "label": deg(f["supporting_knee_angle"])}],
            "math": [
                ["Knee angle (hip–knee–ankle)", deg(f["supporting_knee_angle"])],
                ["Knee direction", bend],
                ["Target", f"{T['supporting_knee_straight']}° or more is straight; hyperextension is fine down to {T['hyperextension_limit']}°"],
            ],
        }

    if key == "working_straight":
        if f["working_knee_angle"] >= T["working_knee_straight"]:
            bend = "straight"
        else:
            bend = "forward (bent)" if f["working_knee_bends_wrong_way"] else "backward (hyperextension)"
        return {
            "shapes": [{"type": "angle", "points": [pt(W["hip"]), pt(W["knee"]), pt(W["ankle"])],
                        "label": deg(f["working_knee_angle"])}],
            "math": [
                ["Knee angle (hip–knee–ankle)", deg(f["working_knee_angle"])],
                ["Knee direction", bend],
                ["Target", f"{T['working_knee_straight']}° or more (180° is perfectly straight)"],
            ],
        }

    if key == "working_height":
        return {
            "shapes": [{"type": "angle", "points": [pt(S["ankle"]), pt(W["hip"]), pt(W["ankle"])],
                        "label": deg(f["working_leg_height"])}],
            "math": [
                ["Leg height (supporting ankle–hip–working ankle)", deg(f["working_leg_height"])],
                ["Target", f"more than {T['height_goal']}°"],
            ],
        }

    if key == "working_wing":
        return {
            "shapes": [{"type": "angle", "points": [pt(W["knee"]), pt(W["ankle"]), pt(W["foot"])],
                        "label": deg(f["wing_deg"])}],
            "math": [
                ["Foot angle (knee–ankle–toe)", deg(f["wing_deg"])],
                ["Target", f"between {T['wing_low']}° and 180°"],
            ],
        }

    if key == "working_rotated":
        return {
            "shapes": [{"type": "perp", "points": [pt(W["heel"]), pt(W["ankle"]), pt(W["foot"])]}],
            "math": [
                ["Heel distance from the ankle–toe line", f"{f['working_heel_offset']:.2f} × foot length"],
                ["Target", f"{T['heel_offset']:.2f} × foot length or less (heel hidden)"],
            ],
        }

    if key == "hips_square":
        return {
            "shapes": [{"type": "segment", "points": [pt(23), pt(24)], "label": f"{f['hip_separation']:.2f}"},
                       {"type": "reference", "points": [HIP_MID, SHOULDER_MID]}],
            "math": [
                ["Distance between hips", f"{f['hip_separation']:.2f} × torso length"],
                ["Target", f"{T['hip_separation']:.2f} × torso length or less"],
            ],
        }

    if key == "chest_lifted":
        return {
            "shapes": [{"type": "from_vertical", "points": [HIP_MID, SHOULDER_MID], "facing": facing,
                        "label": deg(f["torso_lean"])}],
            "math": [
                ["Torso tilt (hips to shoulders)", f"{deg(f['torso_lean'])} forward from vertical"],
                ["Target", f"{T['torso_lean']}° or less"],
            ],
        }

    if key == "sternum_head":
        lean = f["sternum_head_lean"]
        return {
            "shapes": [{"type": "from_vertical", "points": [SHOULDER_MID, HEAD_CENTER], "facing": facing,
                        "label": deg(abs(lean))}],
            "math": [
                ["Sternum-to-head line", f"{deg(abs(lean))} {'forward' if lean > 0 else 'back'} from vertical"],
                ["Target", f"within {T['sternum_head']}° of vertical"],
            ],
        }

    if key == "back_square":
        return {
            "shapes": [{"type": "segment", "points": [pt(11), pt(12)], "label": f"{f['shoulder_separation']:.2f}"},
                       {"type": "reference", "points": [HIP_MID, SHOULDER_MID]}],
            "math": [
                ["Distance between shoulders", f"{f['shoulder_separation']:.2f} × torso length"],
                ["Target", f"{T['shoulder_separation']:.2f} × torso length or less"],
            ],
        }

    if key == "head_gaze":
        shapes = [{"type": "from_horizontal", "points": [HEAD_CENTER, pt(0)], "facing": facing,
                   "label": deg(f["gaze_angle"])}]
        math = [["Gaze (center of head to nose)", f"{deg(f['gaze_angle'])} above level"]]
        if f.get("_first_arabesque"):
            shapes.append({"type": "ray", "points": [HEAD_CENTER, pt(F["index"])]})
            math.append(["Front fingertip", f"{deg(f['finger_angle_from_head'])} above level (gaze should be at or above it)"])
        math.append(["Target", f"{T['gaze_min']}° to {T['gaze_max']}° above level"])
        return {"shapes": shapes, "math": math}

    if key == "front_arm_angle":
        return {
            "shapes": [{"type": "from_horizontal", "points": [pt(F["shoulder"]), pt(F["index"])], "facing": facing,
                        "label": deg(f["front_arm_angle"])}],
            "math": [
                ["Arm angle (shoulder to top of hand)", f"{deg(f['front_arm_angle'])} above horizontal"],
                ["Target", f"{T['front_arm_min']}° to {T['front_arm_max']}°"],
            ],
        }

    if key == "front_wrist":
        return {
            "shapes": [{"type": "angle", "points": [pt(F["elbow"]), pt(F["wrist"]), pt(F["index"])],
                        "label": deg(f["front_wrist_angle"])}],
            "math": [
                ["Wrist angle (arm–wrist–fingers)", deg(f["front_wrist_angle"])],
                ["Target", f"{T['wrist_min']}° to {T['wrist_max']}° (about 150°)"],
            ],
        }

    if key == "front_elbow":
        return {
            "shapes": [{"type": "angle", "points": [pt(F["shoulder"]), pt(F["elbow"]), pt(F["wrist"])],
                        "label": deg(f["front_elbow_angle"])}],
            "math": [
                ["Elbow angle (shoulder–elbow–wrist)", deg(f["front_elbow_angle"])],
                ["Target", f"{T['elbow_min']}° to {T['elbow_max']}° (slightly less than 180°)"],
            ],
        }

    if key == "side_below":
        b = f["side_wrist_below_shoulder"]
        return {
            "shapes": [{"type": "level", "points": [pt(A["shoulder"]), pt(A["wrist"])]}],
            "math": [
                ["Wrist position", f"{abs(b):.2f} × torso length {'below' if b > 0 else 'above'} the shoulder"],
                ["Target", "wrist below the shoulder"],
            ],
        }

    if key == "side_straight":
        return {
            "shapes": [{"type": "angle", "points": [pt(A["shoulder"]), pt(A["elbow"]), pt(A["wrist"])],
                        "label": deg(f["side_elbow_angle"])}],
            "math": [
                ["Arm angle (shoulder–elbow–wrist)", deg(f["side_elbow_angle"])],
                ["Target", f"{T['side_elbow']}° or more (180° is perfectly straight)"],
            ],
        }

    return {"shapes": [], "math": []}
