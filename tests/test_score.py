"""The scorer must reward a correct answer and punish specific, realistic failures."""
import json
from pathlib import Path

from harness.score import score

TASK = json.loads(Path("corpus/tasks/m1_multi_006.json").read_text())
# m1_multi_006: 2 s4 sites -> 4 markers, 2 problems, each {M1.b, M1.e}, fix >= 0.22 um.


def perfect():
    return {"problems": [
        {"id": 1, "rules": ["M1.b", "M1.e"], "location_um": [0.55, 5.0], "fix_min_gap_um": 0.22},
        {"id": 2, "rules": ["M1.b", "M1.e"], "location_um": [5.55, 5.0], "fix_min_gap_um": 0.22},
    ]}


def test_perfect_answer_scores_one():
    s = score(TASK, perfect())
    assert s["f1"] == 1.0
    assert s["rule_accuracy"] == 1.0
    assert s["fix_validity"] == 1.0
    assert s["count_error"] == 0


def test_one_problem_per_marker_is_punished():
    """The failure this benchmark exists to detect: 4 markers read as 4 problems."""
    ans = {"problems": [
        {"id": 1, "rules": ["M1.b"], "location_um": [0.55, 5.0]},
        {"id": 2, "rules": ["M1.e"], "location_um": [0.55, 5.0]},
        {"id": 3, "rules": ["M1.b"], "location_um": [5.55, 5.0]},
        {"id": 4, "rules": ["M1.e"], "location_um": [5.55, 5.0]},
    ]}
    s = score(TASK, ans)
    assert s["count_error"] == 2
    assert s["precision"] == 0.5      # only 2 of 4 can match
    assert s["recall"] == 1.0
    assert s["rule_accuracy"] == 0.0  # each lists one rule, truth has two


def test_wrong_location_does_not_match():
    ans = {"problems": [
        {"id": 1, "rules": ["M1.b", "M1.e"], "location_um": [200.0, 200.0]},
    ]}
    s = score(TASK, ans)
    assert s["matched"] == 0
    assert s["f1"] == 0.0


def test_duplicate_locations_cannot_inflate_recall():
    ans = {"problems": [
        {"id": i, "rules": ["M1.b", "M1.e"], "location_um": [0.55, 5.0]} for i in range(5)
    ]}
    s = score(TASK, ans)
    assert s["matched"] == 1          # one ground-truth problem, claimed once


def test_malformed_answer_scores_zero():
    for bad in (None, {}, {"problems": "lots"}, []):
        s = score(TASK, bad)
        assert s["parse_ok"] is False
        assert s["f1"] == 0.0


CLUSTER_TASK = json.loads(Path("corpus/tasks/m1_cluster_001.json").read_text())
# m1_cluster_001: 160 off-grid markers, 1 problem, fix = snap pitch to 15.0 x 15.0 um.


def _cluster_location():
    """A point inside the clustering task's only problem."""
    mid = next(iter(CLUSTER_TASK["ground_truth"]["marker_to_problem"]))
    parts = mid.rsplit("@", 1)[1].split(",")
    x0, y0, x1, y1 = (float(v) for v in parts)
    return [(x0 + x1) / 2, (y0 + y1) / 2]


def test_correct_pitch_fix_scores_one():
    ans = {"problems": [{"id": 1, "rules": ["metal1_drw_Offgrid"],
                         "location_um": _cluster_location(),
                         "fix_pitch_um": [15.0, 15.0]}]}
    s = score(CLUSTER_TASK, ans)
    assert s["fix_type"] == "snap_array_pitch"
    assert s["f1"] == 1.0
    assert s["fix_validity"] == 1.0


def test_wrong_pitch_fix_scores_zero():
    ans = {"problems": [{"id": 1, "rules": ["metal1_drw_Offgrid"],
                         "location_um": _cluster_location(),
                         "fix_pitch_um": [15.002, 15.002]}]}   # unchanged pitch
    s = score(CLUSTER_TASK, ans)
    assert s["fix_validity"] == 0.0


def test_gap_fix_on_pitch_task_is_not_credited():
    """A spacing fix does not repair an off-grid pitch."""
    ans = {"problems": [{"id": 1, "rules": ["metal1_drw_Offgrid"],
                         "location_um": _cluster_location(),
                         "fix_min_gap_um": 0.22}]}
    s = score(CLUSTER_TASK, ans)
    assert s["fix_validity"] == 0.0
