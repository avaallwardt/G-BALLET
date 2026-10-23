# Step 1: identify landmarks with pose estimation model (mediapipe)

# Goal: turn image pixels into body landmark coordinates
# We need a pose estimation model: a computer-vision model trained to locate body joints / landmarks in an image
# MediaPipe Pose Landmarker returns 33 landmarks (shoulders, hips, knees, etc.)

# Each landmark needs an identity (what it represents), a position (its x, y coordinates in the image), depth (optional), confidence values (how trustworthy the detection is)
# MediaPipe gives landmarks by fixed index (e.g. index 25 always means left knee)
# We should normalize coordinates to make them resolution-independent across images --> that way we can reuse geometry and coordinate thresholds across images of different resolutions
# Normalizing coordinates also enables us to use relative position within an image

from dataclasses import dataclass
from pathlib import Path

# MediaPipe, numpy and Pillow are only needed when this file runs the detector itself (cli.py, tests).
# On the website, MediaPipe runs in the browser and this Python code receives the landmarks, so these
# imports are allowed to be missing there.
try:
    import numpy as np
    from PIL import Image, ImageOps

    # Import MediaPipe library (will import from venv currently running with, will use mediapipe version installed there)
    import mediapipe as mp

    # Import general machinery for running MediaPipe models in Python (contains BaseOptions while tells MediaPipe which model file to use)
    from mediapipe.tasks import python

    # Import code used to load and run MediaPipe vision models, such as LandMarker class (which loads and uses a Pose model)
    from mediapipe.tasks.python import vision
except ImportError:
    mp = None


# See what each each landmark in mediapipe represents
# https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker
NOSE = 0
LEFT_EAR, RIGHT_EAR = 7, 8

# The same body part on each side. Right-side index is always left-side index + 1.
LEFT = dict(shoulder=11, elbow=13, wrist=15, index=19, hip=23, knee=25, ankle=27, heel=29, foot=31)
RIGHT = dict(shoulder=12, elbow=14, wrist=16, index=20, hip=24, knee=26, ankle=28, heel=30, foot=32)

MODEL_PATH = Path(__file__).resolve().parent.parent / "pose_landmarker_full.task"

_detector = None


def get_detector():
    # the detector is created once and reused, so the website doesn't reload the model on every upload
    global _detector
    if _detector is None:
        # Load pose model (file containing learned weights/parameters) (choose model file)
        base_options = python.BaseOptions(
            model_asset_path=str(MODEL_PATH) # download from Google's MediaPipe website
        ) # find the trained pose model file to use when we create the MediaPipe task

        # Create instructions for how detector should work (choose how to run detector)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_poses=1
        )

        # Load detector (runs inference with the pose model using the weights of the model), is an instance of PoseLandmarker (create detector object)
        _detector = vision.PoseLandmarker.create_from_options(options)
    return _detector


@dataclass
class Point:
    # a landmark with x and y in the same units, so it works with angle_at, cross, dist, etc.
    x: float
    y: float
    visibility: float = 1.0


def load_image(file):
    '''
    Load an uploaded photo for MediaPipe.

    However, this calculation assumes the image has proper orientation -- phone photos often store
    "rotate me" in their EXIF data instead of actually being rotated, so we apply that rotation first.
    '''
    pil = Image.open(file)
    pil = ImageOps.exif_transpose(pil).convert("RGB")
    return pil, mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(pil))


def detect_landmarks(file):
    '''
    Returns (raw, points, width, height), or None if no pose was found.

    raw:    MediaPipe's NormalizedLandmark objects (x divided by image width, y divided by image height)
    points: the same landmarks with x rescaled to units of image height.
            Normalized x and y are divided by different numbers on a non-square photo, so one unit of x
            isn't the same length as one unit of y, and that skews angles. Multiplying x by width/height
            puts both in the same units -- still resolution-independent.
    '''
    pil, image = load_image(file)

    # Apply detector to image to get landmarks of image, store in result; contains MediaPipe's predictions, including detected pose landmarks as an attribute (other possible attribute is pose_world_landmarks for estimated 3D coordinates in real world sppace but we didn't enable)
    result = get_detector().detect(image)

    if not result.pose_landmarks:
        return None

    # Get first detected pose/person
    landmarks = result.pose_landmarks[0]

    width, height = pil.size
    return landmarks, to_points(landmarks, width, height), width, height


def to_points(landmarks, width, height):
    '''
    Same landmarks with x rescaled to units of image height (see detect_landmarks).
    Used both here and on the website, where the landmarks come from MediaPipe running in the browser.
    '''
    aspect = width / height
    return [Point(l.x * aspect, l.y, l.visibility if l.visibility is not None else 1.0) for l in landmarks]
