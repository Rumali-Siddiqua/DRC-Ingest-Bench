"""Rebuild each task's layout from its JSON, run DRC, and compare with expected_counts.
Then apply the ground-truth fix and require zero violations."""
import importlib
import json
import sys
from pathlib import Path

from harness.drc_check import DECK_OPTIONS, run_drc


def build_gds(lay, args, suffix=""):
    gds = Path(lay["gds"])
    if suffix:
        gds = gds.with_name(gds.stem + suffix + gds.suffix)
    gds.parent.mkdir(parents=True, exist_ok=True)
    gen = importlib.import_module(lay["generator"])
    gen.build(top_name=lay["topcell"], **args).write(str(gds))
    return gds


def validate(task_path):
    task = json.loads(Path(task_path).read_text())
    lay, drc, fix = task["layout"], task["drc"], task["ground_truth"]["fix"]
    out = Path("experiments/validate") / task["id"]

    if drc["options"] != DECK_OPTIONS:
        return False, f"deck options {drc['options']} differ from helper {DECK_OPTIONS}"

    # 1. The broken layout must report exactly the expected markers.
    counts, _ = run_drc(build_gds(lay, lay["args"]), lay["topcell"], out / "broken")
    if counts != drc["expected_counts"]:
        return False, f"broken: expected {drc['expected_counts']}, got {counts}"

    # 2. The fixed layout must be clean.
    if "layout_args" not in fix:
        return False, "no fix.layout_args in task"
    fixed_args = {**lay["args"], **fix["layout_args"]}
    fixed_counts, _ = run_drc(build_gds(lay, fixed_args, "_fixed"), lay["topcell"], out / "fixed")
    if fixed_counts:
        return False, f"fix does not clear DRC: {fixed_counts}"

    return True, f"{counts} -> fixed clean"


if __name__ == "__main__":
    paths = sys.argv[1:] or sorted(Path("corpus/tasks").glob("*.json"))
    failed = 0
    for p in paths:
        ok, msg = validate(p)
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {Path(p).stem:20s} {msg}")
    print(f"\n{len(paths) - failed}/{len(paths)} tasks pass")
    sys.exit(1 if failed else 0)
