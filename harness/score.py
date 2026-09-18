"""Score a model answer against a task's ground truth (see docs/answer_format.md)."""
import json
import re
from pathlib import Path

TOLERANCE_UM = 1.0
MARKER_ID = re.compile(r"^(?P<rule>.+)@(?P<x0>[-\d.]+),(?P<y0>[-\d.]+),(?P<x1>[-\d.]+),(?P<y1>[-\d.]+)$")


def truth_problems(task):
    """Ground-truth problems as {pid: {rules, marker_count, boxes}}."""
    gt = task["ground_truth"]
    boxes = {}
    for mid, pid in gt["marker_to_problem"].items():
        m = MARKER_ID.match(mid)
        if m:
            boxes.setdefault(pid, []).append(
                (float(m["x0"]), float(m["y0"]), float(m["x1"]), float(m["y1"])))
    return {pid: {**info, "boxes": boxes.get(pid, [])} for pid, info in gt["problems"].items()}


def distance_to_boxes(pt, boxes):
    """Shortest distance from a point to any of the boxes (0 if inside one)."""
    x, y = pt
    best = float("inf")
    for x0, y0, x1, y1 in boxes:
        dx = max(x0 - x, 0.0, x - x1)
        dy = max(y0 - y, 0.0, y - y1)
        best = min(best, (dx * dx + dy * dy) ** 0.5)
    return best


def score(task, answer):
    truth = truth_problems(task)
    required_gap = task["ground_truth"]["fix"].get("min_gap_um")

    if not isinstance(answer, dict) or not isinstance(answer.get("problems"), list):
        return {"parse_ok": False, "precision": 0.0, "recall": 0.0, "f1": 0.0,
                "rule_accuracy": 0.0, "fix_validity": 0.0,
                "reported": 0, "truth": len(truth), "count_error": -len(truth)}

    reported = answer["problems"]

    # Every (reported, truth) pair within tolerance, nearest first, each used once.
    pairs = []
    for i, p in enumerate(reported):
        loc = p.get("location_um")
        if not (isinstance(loc, (list, tuple)) and len(loc) == 2):
            continue
        for pid, info in truth.items():
            d = distance_to_boxes((float(loc[0]), float(loc[1])), info["boxes"])
            if d <= TOLERANCE_UM:
                pairs.append((d, i, pid))

    used_r, used_t, matches = set(), set(), []
    for d, i, pid in sorted(pairs):
        if i in used_r or pid in used_t:
            continue
        used_r.add(i)
        used_t.add(pid)
        matches.append((i, pid))

    n_match = len(matches)
    precision = n_match / len(reported) if reported else 0.0
    recall = n_match / len(truth) if truth else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    rules_ok = sum(
        1 for i, pid in matches
        if sorted(str(r) for r in reported[i].get("rules", [])) == sorted(truth[pid]["rules"]))
    fix_ok = sum(
        1 for i, _ in matches
        if required_gap is not None
        and isinstance(reported[i].get("fix_min_gap_um"), (int, float))
        and reported[i]["fix_min_gap_um"] >= required_gap)

    return {
        "parse_ok": True,
        "reported": len(reported),
        "truth": len(truth),
        "count_error": len(reported) - len(truth),
        "matched": n_match,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "rule_accuracy": round(rules_ok / n_match, 4) if n_match else 0.0,
        "fix_validity": round(fix_ok / n_match, 4) if n_match else 0.0,
    }


def score_file(task_path, answer_path):
    task = json.loads(Path(task_path).read_text())
    try:
        answer = json.loads(Path(answer_path).read_text())
    except json.JSONDecodeError:
        answer = None
    return score(task, answer)
