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
