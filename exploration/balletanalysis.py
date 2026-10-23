# This file will process an image and label it with pose landmarks


# Goal: turn image pixels into body landmark coordinates
# We need a pose estimation model: a computer-vision model trained to locate body joints / landmarks in an image
# MediaPipe Pose Landmarker returns 33 landmarks (shoulders, hips, knees, etc.)


# Goal 1: Use MediaPipe to get landmarks from the photo
# Each landmark needs an identity (what it represents), a position (its x, y coordinates in the image), depth (optional), confidence values (how trustworthy the detection is)
# MediaPipe gives landmarks by fixed index (e.g. index 25 always means left knee)
# We should normalize coordinates to make them resolution-independent across images --> that way we can reuse geometry and coordinate thresholds across images of different resolutions
# Normalizing coordinates also enables us to use relative position within an image

# Calling MediaPipe on the image
# We need to see how MediaPipe's pose landmarker API is called

# Load MediaPipe into Python environment
'''
in terminal:
python3 -m pip install mediapipe
[click yes to create virtual environment, project-specific python installation space, project can have own versions of mediapipe, opencv, etc. without interfering with packages used by other projects]
source .venv/bin/activate [activate venv]
python3 -m pip install mediapipe
python3 balletanalysis.py [run script]

[install correct mediapipe version to match python 3.14]
deactivate
rm -rf .venv
/usr/local/bin/python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install mediapipe==0.10.35


'''

# Import MediaPipe library (will import from venv currently running with, will use mediapipe version installed there)
import mediapipe as mp

# Import general machinery for running MediaPipe models in Python (contains BaseOptions while tells MediaPipe which model file to use)
from mediapipe.tasks import python

# Import code used to load and run MediaPipe vision models, such as LandMarker class (which loads and uses a Pose model)
from mediapipe.tasks.python import vision

# Load pose model (file containing learned weights/parameters) (choose model file)
base_options = python.BaseOptions(
    model_asset_path="pose_landmarker_full.task" # download from Google's MediaPipe website
) # find the trained pose model file to use when we create the MediaPipe task

# Create instructions for how detector should work (choose how to run detector)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE,
    num_poses=1
)

# Load detector (runs inference with the pose model using the weights of the model), is an instance of PoseLandmarker (create detector object)
detector = vision.PoseLandmarker.create_from_options(options)

# Load image (input into model)
image = mp.Image.create_from_file("tori-arabesque.jpg")

# Apply detector to image to get landmarks of image, store in result; contains MediaPipe's predictions, including detected pose landmarks as an attribute (other possible attribute is pose_world_landmarks for estimated 3D coordinates in real world sppace but we didn't enable)
result = detector.detect(image)

# print the landmark coordinates (one detected pose, 33 NormalizedLandmark obects inside of it)
print(result.pose_landmarks)

# Each NormalizedLandmark object contains
# 1. x, y = normalized image position
# 2. estimated depth
# 3. visibility = how likely the landmark is visible
# 4. presence = how likely the landmark is actually present

# Get first detected pose/person
landmarks = result.pose_landmarks[0]

# Extract the 6 leg points (indices from MediaPipe fixed landmark ordering)
left_hip = landmarks[23]
right_hip = landmarks[24]

left_knee = landmarks[25]
right_knee = landmarks[26]

left_ankle = landmarks[27]
right_ankle = landmarks[28]

left_foot = landmarks[31]
right_foot = landmarks[32]
left_heel = landmarks[29]
right_heel = landmarks[30]

print(left_knee)

# Metric 1: Working Leg Straight

# Determine which leg is working leg
# Y-coordinate increases downward
# So the ankle with the smaller y-coordinate is higher in the image and therefore is the working leg
# However, this calculation assumes the image has proper orientation
if left_ankle.y < right_ankle.y:
    working_leg = "left"
else:
    working_leg = "right"


print(f"Working leg is {working_leg}")

# Compute the knee angle (determine how bent the knee is)
# Need 2 vectors: knee-hip and knee-ankle
# Compute angle bewteen them
# cos(theta) = u dot v / |u||v|

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

    angle_radians = math.acos(cos) # arccos ensures we get the principal angle between the two vectors (btwn 0 and 180)
    angle_degrees = math.degrees(angle_radians)

    return angle_degrees

if working_leg == "left":
    working_angle = angle_at(left_hip, left_knee, left_ankle)
else:
    working_angle = angle_at(right_hip, right_knee, right_ankle)

if working_angle > 175.0:
    print("Working leg is straight!")


# Metric 2: Working Leg Height
# Goal: want height above 90 degrees
# Look at angle between hip - supporting ankle and hip - working ankle

if working_leg == "left":
    # supporting leg is right
    height = angle_at(right_ankle, left_hip, left_ankle)
else:
    # supporting leg is left
    height = angle_at(left_ankle, right_hip, right_ankle)

if height > 90:
    print(f"Yay a high leg! Your leg is at {height:.0f} degrees.")


# Metric 3: Working Foot Wing
if working_leg == "left":
    wing_deg = angle_at(left_knee, left_ankle, left_foot)
else:
    wing_deg = angle_at(right_knee, right_ankle, right_foot)

print(f"The wing degree is {wing_deg:.0f}")

if 165 < wing_deg < 180:
    print("The working foot is properly winged.")


# Metric 4: Supporting Leg Straight
if working_leg == "left":
    supporting_angle = angle_at(right_hip, right_knee, right_ankle)
else:
    supporting_angle = angle_at(left_hip, left_knee, left_ankle)

if supporting_angle < 180:
    print("Supporting leg is straight!")

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

# Cross product sign that corresponds to hyperextension vs bent knee depends on whether supporting leg is left or right
print(cross(right_hip, right_knee, right_ankle))

if working_leg == "left":
    # right is supporting leg
    # want principal angle to open to left
    # cross product should be negative
    supporting_angle = angle_at(right_hip, right_knee, right_ankle)
    supporting_cross = cross(right_hip, right_knee, right_ankle)
    if supporting_cross < 0:
        if supporting_angle < 170:
            print("Overhyperextended")
        else:
            print("Good hyperextension")
    else:
        print("Supporting knee bent.")
else:
    # left is supporting leg
    # want principal angle to open to right
    # cross product should be positive
    supporting_angle = angle_at(left_hip, left_knee, left_ankle)
    supporting_cross = cross(left_hip, left_knee, left_ankle)
    if supporting_cross > 0:
        if supporting_angle < 170:
            print("Overhyperextended")
        else:
            print("Good hyperextension")
    else:
        print("Supporting knee bent.")


# MODIFY Metric 1: Working Leg Straight
# Previous:
print("Previous working leg straight")
if working_leg == "left":
    working_angle = angle_at(left_hip, left_knee, left_ankle)
else:
    working_angle = angle_at(right_hip, right_knee, right_ankle)

if working_angle > 175.0:
    print("Working leg is straight!")

# New:
print("\nNew working leg straight")
print(f"working leg is {working_leg}")
if working_leg == "left":
    # cross negative ==> hyperextension
    # cross positive ==> bent knee
    working_angle = angle_at(left_hip, left_knee, left_ankle)
    working_cross = cross(left_hip, left_knee, left_ankle)
    if working_cross > 0:
        print("Bent working leg (and possibly turned in)")
    else:
        print("Straight working leg")
else:
    working_angle = angle_at(right_hip, right_knee, right_ankle)
    working_cross = cross(right_hip, right_knee, right_ankle)
    if working_cross < 0:
        print("Bent working leg (and possibly turned in)")
    else:
        print("Straight working leg")


# Metric 5: Supporting leg turnout
# With more turnout, the heel moves behind the ankle from 2D perspective, so the ankle-heel-toe triangle collapses

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

# From experimentation with turned in and turned out supporting legs
    # turned in max : triangle area: ~ 0.0009
    # turned out max: triangle area: ~ 0.0001
# We will say turned out supporting leg is 0.0004 and below, else is turned in

if working_leg == "left":
    # supporting leg is right
    area = triangle_area(right_ankle, right_heel, right_foot)
    if area < 0.004:
        print("Good supporting leg turnout.")
    else:
        print("Turned in supporting leg.")
else:
    # supporting leg is left
    area = triangle_area(left_ankle, left_heel, left_foot)
    if area > 0.004:
        print("Good supporting leg turnout.")
    else:
        print("Turned in supporting leg.")

# Problem: This criteria can be camera angle dependent



# Metric 6: Working leg turnout
# More rotation --> more of heel hidden behind ankle

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


print("\nV1: heel to ankle distance")
# From experimentation
    # best turnout --> dist = 0.0235
    # good turnout --> dist = 0.0144
    # poor turnout --> dist = 0.0163
if working_leg == 'left':
    print(dist(left_ankle, left_heel))
else:
    print(dist(right_ankle, right_heel))

print("\nV2: heel to ankle distance normalized by foot length")
# From experimentation
    # best turnout (ava)   --> val = 0.2419
    # great turnout (tori) --> val = 0.211
    # good turnout (grace) --> val = 0.1786
    # poor turnout (daija) --> val = 0.185
# Unexpected results because better turnout should yield a lower heel_gap_ratio not a higher one
if working_leg == 'left':
    heel_gap_ratio = dist(left_ankle, left_heel) / dist(left_ankle, left_foot)
    print(heel_gap_ratio)
else:
    heel_gap_ratio = dist(right_ankle, right_heel) / dist(right_ankle, right_foot)
    print(heel_gap_ratio)

print("\nV3: perpendicular distance from heel to ankle-toe line")

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

    # draw p_line
    p_line =

    # find intersection of new line with a-b line


    # find distance from p to point of intersection
