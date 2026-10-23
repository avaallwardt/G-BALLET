# End-to-end check on the example photo (needs mediapipe installed)
#   python3 -m pytest

from pathlib import Path

import pytest

pytest.importorskip("mediapipe")

from analysis import analyze  # noqa: E402

EXAMPLE = Path(__file__).resolve().parent.parent / "samples" / "example-arabesque.jpg"


def test_example_photo_is_an_arabesque():
    result = analyze(str(EXAMPLE))
    assert result["is_arabesque"]
    assert result["summary"]["first_arabesque"]
    assert result["summary"]["scored"] == 16


def test_every_criterion_has_feedback():
    result = analyze(str(EXAMPLE))
    for element in result["elements"]:
        for c in element["constraints"]:
            assert c["feedback"]
            assert c["score"] in {"good", "moderate", "major", "na"}


def test_not_a_photo():
    result = analyze(__file__)
    assert not result["is_arabesque"]
    assert result["reason"] == "unreadable"
