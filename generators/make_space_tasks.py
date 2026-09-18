"""The two original single-injection spacing tasks (the first hand-built tasks).

Marker counts were measured with the frozen environment in docs/environment.md.
"""
import json
from pathlib import Path

ENV = {
    "deck": "IHP-Open-PDK sg13g2 KLayout (run_drc.py)",
    "options": ["--no_density", "--run_mode=flat"],
    "klayout_version": "0.30.7",
    "klayout_python": "0.30.12",
    "pdk_commit": "5e6d592e4002946a4616f798c357f0f3c06cf3b6",
}

SPECS = [
    ("m1_space_001", 0.10, 0.5, {"M1.b": 1},
     "Wire 1 is placed 0.10 um from wire 0. The report shows M1.b (0.18 um minimum)."),
    ("m1_space_002", 0.20, 0.2, {"M1.e": 1},
     "Narrow wire 1 (0.2 um) is 0.20 um from wide wire 0 (0.5 um) over a 10 um parallel "
     "run. The report shows M1.e (0.22 um required)."),
]

out_dir = Path("corpus/tasks")
out_dir.mkdir(parents=True, exist_ok=True)

for task_id, gap, width1, counts, cause_text in SPECS:
    artifact = 0.22 if "M1.e" in counts else 0.18
    task = {
        "id": task_id,
        "version": 1,
        "rule_family": "metal1_spacing",
        "task_type": "root_cause",
        "layout": {
            "generator": "generators.inject_spacing",
            "args": {"gap": gap, "width1": width1},
            "gds": f"corpus/inject/{task_id}.gds",
            "topcell": task_id,
        },
        "drc": {**ENV, "expected_counts": counts},
        "ground_truth": {
            "distinct_problems": 1,
            "total_markers": sum(counts.values()),
            "root_cause": cause_text,
            "rules_involved": sorted(counts),
            "cause": {"type": "spacing", "gap_um": gap,
                      "artifact_required_gap_um": artifact, "spec_required_gap_um": 0.22},
            "fix": {"type": "set_min_gap",
                    "action": "move wire 1 in +x",
                    "artifact_value_um": artifact,
                    "spec_value_um": 0.22,
                    "layout_args": {"gap": 0.22}},
            "known_deck_discrepancy": artifact != 0.22,
        },
        "notes": ("Original single-injection task. See docs/results_phase3.md for the M1.e "
                  "deck behaviour on wide-vs-wide geometry."),
    }
    (out_dir / f"{task_id}.json").write_text(json.dumps(task, indent=2) + "\n")
    print("wrote", task_id, counts)
