# Step 4: Feedback
# Use the criteria scores/evaluation to generate feedback for the dancer
#
# Every piece of text the website shows lives here, so wording can be changed in one place.

# Criteria, in the order of the technique rules table.
ELEMENTS = {
    "supporting_leg": "Supporting Leg",
    "working_leg": "Working Leg",
    "hips": "Hips",
    "chest_back": "Chest & Back",
    "head": "Head",
    "front_arm": "Arm in Front of Body for 1st Arabesque",
    "side_arm": "Arm to Side of Body",
}

CONSTRAINTS = {
    "supporting_rotated": "Rotated (sole of shoe at least partially showing)",
    "supporting_knee": "Knee straight",
    "working_straight": "Working Leg Straight",
    "working_height": "Working Leg Height",
    "working_wing": "Knee-angle-toe angle (slightly winged foot, penalize over-winging too!)",
    "working_rotated": "Rotated, heel not visible from underrotation or overrotation",
    "hips_square": "Square",
    "chest_lifted": "Lifted and supported",
    "sternum_head": "Sternum to center of head should be vertical line relative to rest of arabesque",
    "back_square": "Back is square",
    "head_gaze": "Looking slightly upward over the finger",
    "front_arm_angle": "25-30 degree angle from shoulder to top of hand",
    "front_wrist": "Angle from arm-wrist-fingers should not be 180 degrees",
    "front_elbow": "Slight break in elbow too",
    "front_fingers": "Fingers soft",
    "side_below": "Below shoulder",
    "side_straight": "Shoulder-elbow-wrist angle should be 180 degrees",
    "side_fingers": "Fingers soft",
}

FEEDBACK = {
    # ---- Supporting Leg ----
    "supporting_knee.straight": "Supporting leg is straight!",
    "supporting_knee.good_hyperextension": "Good hyperextension",
    "supporting_knee.overhyperextended": "Overhyperextended",
    "supporting_knee.slightly_bent": "Lengthen the supporting knee; it appears slightly bent.",
    "supporting_knee.bent": "Supporting knee bent.",

    "supporting_rotated.good": "Good supporting leg turnout.",
    "supporting_rotated.turned_in": "Turned in supporting leg.",
    "supporting_rotated.note": "This criteria can be camera angle dependent.",

    # ---- Working Leg ----
    "working_straight.straight": "Straight working leg",
    "working_straight.bent": "Bent working leg (and possibly turned in)",

    "working_height.high": "Yay a high leg! Your leg is at {height:.0f} degrees.",
    "working_height.almost": "Your leg is at {height:.0f} degrees. Almost there! Lift a little higher to get above 90 degrees.",
    "working_height.low": "Your leg is at {height:.0f} degrees. Lift your leg higher, the goal is above 90 degrees.",

    "working_wing.good": "The wing degree is {wing:.0f}. The working foot is properly winged.",
    "working_wing.not_winged": "The wing degree is {wing:.0f}. The working foot is not properly winged. Aim for a slightly winged foot (between 165 and 180 degrees), but don't over-wing!",

    "working_rotated.good": "Good working leg turnout.",
    "working_rotated.heel_showing": "Heel showing on the working foot, so the working leg may be underrotated or overrotated.",
    "working_rotated.note": "Opening working leg hip may cause medial heel to appear, not enough rotation may cause lateral heel to appear.",

    # ---- Hips ----
    "hips_square.good": "Hips square.",
    "hips_square.open": "Hips not square. Should not be opening hip of working leg.",

    # ---- Chest & Back ----
    "chest_lifted.good": "Chest lifted and supported.",
    "chest_lifted.dropping": "Lift your chest. It should be lifted and supported, and it's tipping forward.",

    "sternum_head.good": "Sternum to center of head is a vertical line.",
    "sternum_head.forward": "Head is in front of the sternum. Sternum to center of head should be vertical line.",
    "sternum_head.back": "Head is behind the sternum. Sternum to center of head should be vertical line.",

    "back_square.good": "Back is square.",
    "back_square.open": "Back not square. Your shoulders should be as close to each other as possible.",
    "back_square.note": "MediaPipe may not let them overlap but they should not be far apart.",

    # ---- Head ----
    "head_gaze.good": "Looking slightly upward over the finger.",
    "head_gaze.too_low": "Look slightly upward over the finger.",
    "head_gaze.too_high": "Looking up too much. Only slightly upward over the finger.",
    "head_gaze.below_finger": "Bring your eyes up and over the finger.",

    # ---- Arm in Front of Body for 1st Arabesque ----
    "front_arm_angle.good": "Front arm is at {angle:.0f} degrees. Right in the 25-30 degree range!",
    "front_arm_angle.low": "Front arm is at {angle:.0f} degrees. Raise it a little, aim for a 25-30 degree angle from shoulder to top of hand.",
    "front_arm_angle.high": "Front arm is at {angle:.0f} degrees. Lower it a little, aim for a 25-30 degree angle from shoulder to top of hand.",

    "front_wrist.good": "Nice break in the wrist.",
    "front_wrist.straight": "Wrist too straight. Angle from arm-wrist-fingers should not be 180 degrees, maybe 150 degrees for break in wrist.",
    "front_wrist.too_broken": "Too much break in the wrist. Aim for about 150 degrees.",

    "front_elbow.good": "Slight break in elbow.",
    "front_elbow.straight": "Elbow locked straight. Slight break in elbow, slightly less than 180 degrees.",
    "front_elbow.too_bent": "Elbow too bent. Only a slight break in elbow, slightly less than 180 degrees.",

    "fingers.unsure": "Fingers soft is not yet scored due to the lack of granularity in finger landmark detection.",

    "front_arm.not_first": "Arms don't look like 1st arabesque, so the arm criteria were skipped.",

    # ---- Arm to Side of Body ----
    "side_below.good": "Side arm is below shoulder.",
    "side_below.too_high": "Side arm should be below shoulder.",
    "side_straight.good": "Side arm is straight.",
    "side_straight.bent": "Lengthen the side arm. Shoulder-elbow-wrist angle should be 180 degrees.",

    # ---- Not visible ----
    "not_visible": "Couldn't see this clearly in the photo, so it wasn't scored.",
}

# Summary lines
SUMMARY = {
    "working_leg": "Working leg: {working_leg}",
    "arm_position": "Arm position: {arm_position}",
    "count": "{good} of {scored} criteria met.",
}

# Criterion score labels -- "supporting leg straightness = moderate issue"
SCORE_LABELS = {
    "good": "good",
    "moderate": "moderate issue",
    "major": "major issue",
    "na": "not scored",
}

# When the photo isn't an arabesque
NOT_ARABESQUE = {
    "no_pose": "We couldn't find a dancer in this photo. Try a photo where your whole body is in the frame!",
    "legs_hidden": "We can't see both legs clearly. Try a photo where your whole body, including your feet, is in the frame.",
    "leg_not_lifted": "This doesn't look like an arabesque. Neither leg is lifted very high. Upload an arabesque photo and we'll take a look!",
    "leg_in_front": "This doesn't look like an arabesque. The lifted leg looks like it's in front of you, and in an arabesque the working leg extends behind you.",
    "not_standing": "This doesn't look like an arabesque. The supporting leg isn't underneath you. Make sure the photo is right side up and your whole body is in the frame!",
    "front_view": "This doesn't look like an arabesque from here. It might be à la seconde, or the photo was taken from the front. Try a side view of your arabesque!",
    "attitude": "This looks more like an attitude than an arabesque. The working knee is bent quite a bit.",
    "unreadable": "We couldn't open that file. Try a JPG or PNG photo.",
}
