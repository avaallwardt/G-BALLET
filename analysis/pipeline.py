# Pipeline: landmarks → interpretable features → criteria scores → feedback
#
# Example
# Image: arabesque photo
# Landmarks: supporting hip, supporting knee, supporting ankle (specific body points)
# Interpretable feature: supporting knee angle = 168 degrees
# Criterion score: supporting leg straightness = moderate issue
# Feedback: "Lengthen the supporting knee; it appears slightly bent."

from .landmarks import detect_landmarks, to_points, Point
from .features import extract_features
from .criteria import check_arabesque, score_criteria, T
from .explain import explain
from .feedback import ELEMENTS, CONSTRAINTS, SUMMARY, SCORE_LABELS, NOT_ARABESQUE


def analyze(file):
    '''
    Input: an image file (path or file-like object)
    Output: a dict the website (or the command line) can show
    '''
    # Step 1: identify landmarks with pose estimation model (mediapipe)
    try:
        detected = detect_landmarks(file)
    except Exception:
        return {"is_arabesque": False, "reason": "unreadable", "message": NOT_ARABESQUE["unreadable"]}

    if detected is None:
        return {"is_arabesque": False, "reason": "no_pose", "message": NOT_ARABESQUE["no_pose"]}
    raw, points, width, height = detected
    return analyze_pose(raw, points)


def analyze_landmarks(landmarks, width, height):
    '''
    Same as analyze(), but starting from landmarks that were already detected
    (the website runs MediaPipe in the browser, then calls this).

    landmarks: list of 33 dicts with x, y (normalized) and visibility -- or an empty list if no pose was found
    '''
    if not landmarks:
        return {"is_arabesque": False, "reason": "no_pose", "message": NOT_ARABESQUE["no_pose"]}
    raw = [Point(l["x"], l["y"], l.get("visibility", 1.0)) for l in landmarks]
    return analyze_pose(raw, to_points(raw, width, height))


def analyze_pose(raw, points):
    '''Steps 2-4, shared by analyze() and analyze_landmarks().'''
    landmarks_out = [{"x": l.x, "y": l.y, "v": l.visibility} for l in raw]

    # Step 2: extract interpretable features from landmarks
    f = extract_features(raw, points)

    reason = check_arabesque(f)
    if reason:
        return {"is_arabesque": False, "reason": reason, "message": NOT_ARABESQUE[reason],
                "landmarks": landmarks_out}

    # Step 3: criteria scores
    scored, first_arabesque = score_criteria(f)
    f["_first_arabesque"] = first_arabesque

    # Step 4: feedback
    elements = []
    good = scored_count = 0
    for key, title in ELEMENTS.items():
        rows = []
        for r in scored[key]:
            r = dict(r, constraint=CONSTRAINTS[r["key"]], score_label=SCORE_LABELS[r["score"]])
            # the geometry behind this score: the calculation, and what to draw on the photo
            r["geometry"] = explain(r["key"], f, T) if r["feature"] else {"shapes": [], "math": []}
            rows.append(r)
            if r["score"] != "na":
                scored_count += 1
                good += r["score"] == "good"
        elements.append({"key": key, "title": title, "constraints": rows})

    return {
        "is_arabesque": True,
        "summary": {
            "working_leg": SUMMARY["working_leg"].format(working_leg=f["working_leg"]),
            "arm_position": SUMMARY["arm_position"].format(
                arm_position="1st arabesque" if first_arabesque else "not 1st arabesque"),
            "count": SUMMARY["count"].format(good=good, scored=scored_count),
            "good": good,
            "scored": scored_count,
            "first_arabesque": first_arabesque,
        },
        "elements": elements,
        "landmarks": landmarks_out,
        "working_leg": f["working_leg"],
        "front_arm": f["front_arm"],
    }
