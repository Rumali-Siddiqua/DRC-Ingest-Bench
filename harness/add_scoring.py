"""Add problems and marker_to_problem to each task, derived from actual DRC output."""
import json
import re
import sys
from pathlib import Path

import klayout.rdb as rdb

from harness.drc_check import run_drc
from harness.validate import build_gds

PITCH_X, PITCH_Y = 5.0, 12.0
NUM = re.compile(r"-?\d+\.?\d*")


def markers(report):
    db = rdb.ReportDatabase("")
    db.load(str(report))
    out = []
    for cat in db.each_category():
        if not cat.num_items():
            continue
        for item in db.each_item_per_category(cat.rdb_id()):
            for v in item.each_value():
                n = [float(x) for x in NUM.findall(v.to_s())]
                xs, ys = n[0::2], n[1::2]
                bb = (min(xs), min(ys), max(xs), max(ys))
                out.append((cat.name(), bb))
    return out


def site_key(bb):
    return (int(bb[1] // PITCH_Y), int(bb[0] // PITCH_X))


def marker_id(rule, bb):
    return f"{rule}@{bb[0]:.3f},{bb[1]:.3f},{bb[2]:.3f},{bb[3]:.3f}"


def add(task_path):
    task = json.loads(Path(task_path).read_text())
    lay = task["layout"]
    gds = build_gds(lay, lay["args"])
    _, report = run_drc(gds, lay["topcell"], Path("experiments/validate") / task["id"] / "scoring")

    ms = markers(report)
    if task.get("task_type") == "clustering" or task["rule_family"] == "offgrid_placement":
        # Every marker shares one root cause: the array pitch.
        groups = {"problem_001": ms}
    else:
        groups = {}
        for rule, bb in ms:
            groups.setdefault(site_key(bb), []).append((rule, bb))
        groups = {f"problem_{i:03d}": v for i, (_, v) in enumerate(sorted(groups.items()), 1)}

    problems, mapping = {}, {}
    for pid, items in groups.items():
        rules = sorted({r for r, _ in items})
        problems[pid] = {"rules": rules, "marker_count": len(items)}
        for rule, bb in items:
            mapping[marker_id(rule, bb)] = pid

    task.setdefault("task_type", "root_cause")
    task["ground_truth"]["problems"] = problems
    task["ground_truth"]["marker_to_problem"] = mapping
    Path(task_path).write_text(json.dumps(task, indent=2) + "\n")

    stated = task["ground_truth"].get("distinct_problems")
    ok = stated == len(problems)
    return ok, f"{len(ms)} markers -> {len(problems)} problems (stated {stated})"


if __name__ == "__main__":
    paths = sys.argv[1:] or sorted(Path("corpus/tasks").glob("*.json"))
    bad = 0
    for p in paths:
        ok, msg = add(p)
        bad += not ok
        print(f"{'OK  ' if ok else 'MISMATCH'} {Path(p).stem:20s} {msg}")
    print(f"\n{len(paths) - bad}/{len(paths)} consistent")
