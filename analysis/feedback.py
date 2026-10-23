# Step 4: Feedback
# Use the criteria scores/evaluation to generate feedback for the dancer
#
# Every piece of text the website shows lives here, so wording can be changed in one place.
# Where each line came from:
#   [code]  copied word for word from a print() in balletanalysis.py
#   [notes] copied word for word from Ballet NN technique rules
#   [new]   no wording existed yet, so it's written to sound like the lines above

# Criteria, in the order of the technique rules table.
# Each element and constraint name is [notes].
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
    "supporting_rotated": "Rotated (sole of shoe at least partially showing)",          # [notes]
    "supporting_knee": "Knee straight",                                                 # [notes]
    "working_straight": "Working Leg Straight",                                         # [code] Metric 1
    "working_height": "Working Leg Height",                                             # [code] Metric 2
    "working_wing": "Knee-angle-toe angle (slightly winged foot, penalize over-winging too!)",  # [notes]
    "working_rotated": "Rotated, heel not visible from underrotation or overrotation",  # [notes]
    "hips_square": "Square",                                                            # [notes]
    "chest_lifted": "Lifted and supported",                                             # [notes]
    "sternum_head": "Sternum to center of head should be vertical line relative to rest of arabesque",  # [notes]
    "back_square": "Back is square",                                                    # [notes] "also need to make sure back is square"
    "head_gaze": "Looking slightly upward over the finger",                             # [notes]
    "front_arm_angle": "25-30 degree angle from shoulder to top of hand",               # [notes] (range updated from 30-45)
    "front_wrist": "Angle from arm-wrist-fingers should not be 180 degrees",            # [notes]
    "front_elbow": "Slight break in elbow too",                                         # [notes]
    "front_fingers": "Fingers soft",                                                    # [notes]
    "side_below": "Below shoulder",                                                     # [notes]
    "side_straight": "Shoulder-elbow-wrist angle should be 180 degrees",                # [notes]
    "side_fingers": "Fingers soft",                                                     # [notes]
}

FEEDBACK = {
    # ---- Supporting Leg ----
    "supporting_knee.straight": "Supporting leg is straight!",                                   # [code]
    "supporting_knee.good_hyperextension": "Good hyperextension",                                # [code]
    "supporting_knee.overhyperextended": "Overhyperextended",                                    # [code]
    "supporting_knee.slightly_bent": "Lengthen the supporting knee; it appears slightly bent.",  # [notes] (the Example)
    "supporting_knee.bent": "Supporting knee bent.",                                             # [code]

    "supporting_rotated.good": "Good supporting leg turnout.",                                   # [code]
    "supporting_rotated.turned_in": "Turned in supporting leg.",                                 # [code]
    "supporting_rotated.note": "This criteria can be camera angle dependent.",                   # [code] "Problem: This criteria can be camera angle dependent"

    # ---- Working Leg ----
    "working_straight.straight": "Straight working leg",                                         # [code]
    "working_straight.bent": "Bent working leg (and possibly turned in)",                        # [code]

    "working_height.high": "Yay a high leg! Your leg is at {height:.0f} degrees.",               # [code]
    "working_height.almost": "Your leg is at {height:.0f} degrees. Almost there! Lift a little higher to get above 90 degrees.",  # [new]
    "working_height.low": "Your leg is at {height:.0f} degrees. Lift your leg higher, the goal is above 90 degrees.",              # [new]

    "working_wing.good": "The wing degree is {wing:.0f}. The working foot is properly winged.",  # [code] (two prints joined)
    "working_wing.not_winged": "The wing degree is {wing:.0f}. The working foot is not properly winged. Aim for a slightly winged foot (between 165 and 180 degrees), but don't over-wing!",  # [new]

    "working_rotated.good": "Good working leg turnout.",                                         # [new] (mirrors your supporting leg line)
    "working_rotated.heel_showing": "Heel showing on the working foot, so the working leg may be underrotated or overrotated.",  # [new]
    "working_rotated.note": "Opening working leg hip may cause medial heel to appear, not enough rotation may cause lateral heel to appear.",  # [notes]

    # ---- Hips ----
    "hips_square.good": "Hips square.",                                                          # [new]
    "hips_square.open": "Hips not square. Should not be opening hip of working leg.",            # [new] + [notes]

    # ---- Chest & Back ----
    "chest_lifted.good": "Chest lifted and supported.",                                          # [new]
    "chest_lifted.dropping": "Lift your chest. It should be lifted and supported, and it's tipping forward.",  # [new]

    "sternum_head.good": "Sternum to center of head is a vertical line.",                        # [new]
    "sternum_head.forward": "Head is in front of the sternum. Sternum to center of head should be vertical line.",  # [new] + [notes]
    "sternum_head.back": "Head is behind the sternum. Sternum to center of head should be vertical line.",         # [new] + [notes]

    "back_square.good": "Back is square.",                                                       # [new]
    "back_square.open": "Back not square. Your shoulders should be as close to each other as possible.",  # [new] + [notes]
    "back_square.note": "MediaPipe may not let them overlap but they should not be far apart.",  # [notes]

    # ---- Head ----
    "head_gaze.good": "Looking slightly upward over the finger.",                                # [notes]
    "head_gaze.too_low": "Look slightly upward over the finger.",                                # [new]
    "head_gaze.too_high": "Looking up too much. Only slightly upward over the finger.",          # [new]
    "head_gaze.below_finger": "Bring your eyes up and over the finger.",                         # [new]

    # ---- Arm in Front of Body for 1st Arabesque ----
    "front_arm_angle.good": "Front arm is at {angle:.0f} degrees. Right in the 25-30 degree range!",                 # [new]
    "front_arm_angle.low": "Front arm is at {angle:.0f} degrees. Raise it a little, aim for a 25-30 degree angle from shoulder to top of hand.",  # [new] + [notes]
    "front_arm_angle.high": "Front arm is at {angle:.0f} degrees. Lower it a little, aim for a 25-30 degree angle from shoulder to top of hand.",  # [new] + [notes]

    "front_wrist.good": "Nice break in the wrist.",                                              # [new]
    "front_wrist.straight": "Wrist too straight. Angle from arm-wrist-fingers should not be 180 degrees, maybe 150 degrees for break in wrist.",  # [new] + [notes]
    "front_wrist.too_broken": "Too much break in the wrist. Aim for about 150 degrees.",         # [new]

    "front_elbow.good": "Slight break in elbow.",                                                # [new]
    "front_elbow.straight": "Elbow locked straight. Slight break in elbow, slightly less than 180 degrees.",  # [new] + [notes] ("ankle" read as elbow)
    "front_elbow.too_bent": "Elbow too bent. Only a slight break in elbow, slightly less than 180 degrees.",  # [new] + [notes]

    "fingers.unsure": "Fingers soft (unsure how to evaluate)",                                   # [notes]

    "front_arm.not_first": "Arms don't look like 1st arabesque, so the arm criteria were skipped.",  # [new]

    # ---- Arm to Side of Body ----
    "side_below.good": "Side arm is below shoulder.",                                            # [new]
    "side_below.too_high": "Side arm should be below shoulder.",                                 # [new] + [notes]
    "side_straight.good": "Side arm is straight.",                                               # [new]
    "side_straight.bent": "Lengthen the side arm. Shoulder-elbow-wrist angle should be 180 degrees.",  # [new] + [notes]

    # ---- Not visible ----
    "not_visible": "Couldn't see this clearly in the photo, so it wasn't scored.",               # [new]
}

# Summary lines
SUMMARY = {
    "working_leg": "Working leg: {working_leg}",                                                 # [code] "Working leg is {working_leg}", reformatted
    "arm_position": "Arm position: {arm_position}",                                             # [new]
    "count": "{good} of {scored} criteria met.",                                             # [new]
}

# Criterion score labels -- "supporting leg straightness = moderate issue" [notes]
SCORE_LABELS = {
    "good": "good",
    "moderate": "moderate issue",
    "major": "major issue",
    "na": "not scored",
}

# When the photo isn't an arabesque (all [new])
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
