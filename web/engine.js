// Runs the analysis in the visitor's browser.
//
//   Step 1 (landmarks):  MediaPipe Pose Landmarker (JavaScript version, same model file as the Python version)
//   Steps 2-4:           the Python code in analysis/, run unchanged with Pyodide (Python compiled for the browser)
//
// Nothing is uploaded anywhere: the photo stays on the visitor's device.

import { FilesetResolver, PoseLandmarker } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.35/vision_bundle.mjs";

const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.29.5/full/";
const MEDIAPIPE_WASM = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.35/wasm";
const PY_FILES = ["geometry.py", "landmarks.py", "features.py", "criteria.py", "feedback.py", "explain.py", "pipeline.py"];

async function loadLandmarker() {
  const vision = await FilesetResolver.forVisionTasks(MEDIAPIPE_WASM);
  return PoseLandmarker.createFromOptions(vision, {
    baseOptions: { modelAssetPath: "pose_landmarker_full.task", delegate: "CPU" },
    runningMode: "IMAGE",
    numPoses: 1,
  });
}

async function loadPython() {
  const { loadPyodide } = await import(PYODIDE_URL + "pyodide.mjs");
  const py = await loadPyodide({ indexURL: PYODIDE_URL });
  py.FS.mkdirTree("/home/pyodide/analysis");
  await Promise.all(PY_FILES.map(async (name) => {
    const res = await fetch(`analysis/${name}?v=${Date.now()}`);
    if (!res.ok) throw new Error(`Couldn't load analysis/${name}`);
    py.FS.writeFile(`/home/pyodide/analysis/${name}`, await res.text());
  }));
  // __init__.py is written here instead of fetched, because GitHub Pages skips files that start with "_"
  py.FS.writeFile("/home/pyodide/analysis/__init__.py", "");
  await py.runPythonAsync(`
import sys, json
sys.path.insert(0, "/home/pyodide")
from analysis.pipeline import analyze_landmarks
from analysis.feedback import NOT_ARABESQUE

def run(landmarks_json, width, height):
    return json.dumps(analyze_landmarks(json.loads(landmarks_json), width, height))
`);
  return py;
}

// Start loading both as soon as the page opens
const landmarkerReady = loadLandmarker();
const pythonReady = loadPython();
export const ready = Promise.all([landmarkerReady, pythonReady]);

// Phone photos often store their pixels sideways plus a "rotate me" tag (EXIF orientation).
// The page displays them upright, but MediaPipe would read the raw sideways pixels, so the photo
// is drawn upright onto a canvas first (drawing applies the rotation), and very large photos are
// scaled down, since some phones can't handle images bigger than 4096 pixels. Landmarks are fractions of the
// width and height, so scaling doesn't change any measurement.
const MAX_SIDE = 4096;

function uprightCanvas(img) {
  const w = img.naturalWidth, h = img.naturalHeight;
  const scale = Math.min(1, MAX_SIDE / Math.max(w, h));
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(w * scale);
  canvas.height = Math.round(h * scale);
  canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
  return canvas;
}

export async function analyzeImage(img) {
  const [landmarker, py] = await ready;
  const canvas = uprightCanvas(img);
  const detection = landmarker.detect(canvas);
  const landmarks = (detection.landmarks && detection.landmarks[0] || [])
    .map((l) => ({ x: l.x, y: l.y, visibility: l.visibility ?? 1 }));
  const out = py.globals.get("run")(JSON.stringify(landmarks), canvas.width, canvas.height);
  return JSON.parse(out);
}

export async function message(key) {
  const [, py] = await ready;
  return py.globals.get("NOT_ARABESQUE").get(key);
}
