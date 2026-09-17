"""Clustering tasks: one root cause (an off-grid array pitch) produces many markers.
Marker counts are taken from measured DRC runs, not predicted."""
import json
from pathlib import Path

STEP = 15.002        # um, 2 nm off the 5 nm grid
STEP_FIXED = 15.0    # um, on grid
MEASURED = {3: 160, 5: 480, 10: 1920, 20: 7680}   # n -> metal1_drw_Offgrid markers

out_dir = Path("corpus/tasks")
out_dir.mkdir(parents=True, exist_ok=True)

for i, (n, markers) in enumerate(sorted(MEASURED.items()), start=1):
    task_id = f"m1_cluster_{i:03d}"
    task = {
        "id": task_id,
        "version": 1,
        "rule_family": "offgrid_placement",
        "task_type": "clustering",
        "layout": {
            "generator": "generators.offgrid_array",
            "args": {"n": n, "step_x_um": STEP, "step_y_um": STEP},
            "gds": f"corpus/multi/{task_id}.gds",
            "topcell": task_id,
        },
        "drc": {
            "deck": "IHP-Open-PDK sg13g2 KLayout (run_drc.py)",
            "options": ["--no_density", "--run_mode=flat"],
            "klayout_version": "0.30.7",
            "expected_counts": {"metal1_drw_Offgrid": markers},
        },
        "ground_truth": {
            "distinct_problems": 1,
            "total_markers": markers,
            "root_cause": (f"The {n}x{n} array pitch is {STEP} um, which is 2 nm off the 5 nm "
                           f"manufacturing grid. Every off-grid instance puts its Metal1 edges "
                           f"off grid. The cell itself is clean."),
            "rules_involved": ["metal1_drw_Offgrid"],
            "fix": {
                "action": f"snap the array pitch to the grid ({STEP_FIXED} um)",
                "layout_args": {"step_x_um": STEP_FIXED, "step_y_um": STEP_FIXED},
            },
        },
        "notes": (f"One root cause, {markers} markers. Control run at {STEP_FIXED} um pitch is DRC clean. "
                  "Marker count measured, not derived."),
    }
    (out_dir / f"{task_id}.json").write_text(json.dumps(task, indent=2) + "\n")

print(f"Wrote {len(MEASURED)} clustering tasks")
