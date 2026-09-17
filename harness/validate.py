"""Rebuild each task's layout from its JSON, run DRC, and compare with expected_counts."""
import importlib
import json
import sys
from pathlib import Path

from harness.drc_check import DECK_OPTIONS, run_drc


def validate(task_path):
    task = json.loads(Path(task_path).read_text())
    lay, drc = task["layout"], task["drc"]

    # The task must use the same deck options as the helper, or results aren't comparable.
    if drc["options"] != DECK_OPTIONS:
        return False, f"deck options {drc['options']} differ from helper {DECK_OPTIONS}"

    gds = Path(lay["gds"])
    gds.parent.mkdir(parents=True, exist_ok=True)
    gen = importlib.import_module(lay["generator"])
    gen.build(top_name=lay["topcell"], **lay["args"]).write(str(gds))

    counts, _ = run_drc(gds, lay["topcell"], Path("experiments/validate") / task["id"])
    if counts != drc["expected_counts"]:
        return False, f"expected {drc['expected_counts']}, got {counts}"
    return True, f"{counts}"


if __name__ == "__main__":
    paths = sys.argv[1:] or sorted(Path("corpus/tasks").glob("*.json"))
    failed = 0
    for p in paths:
        ok, msg = validate(p)
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {Path(p).stem:20s} {msg}")
    print(f"\n{len(paths) - failed}/{len(paths)} tasks pass")
    sys.exit(1 if failed else 0)
