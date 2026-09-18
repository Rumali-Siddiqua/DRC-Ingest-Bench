"""Two tasks at the scale where raw ingestion stops being possible.

Marker counts below were measured with the frozen environment in docs/environment.md and
are baked in, so regenerating reproduces the committed tasks. Re-measure if the PDK or
KLayout version changes."""
import json
from pathlib import Path

out_dir = Path("corpus/tasks")
COMMON = {
    "version": 1,
    "drc": {
        "deck": "IHP-Open-PDK sg13g2 KLayout (run_drc.py)",
        "options": ["--no_density", "--run_mode=flat"],
        "klayout_version": "0.30.7",
        "klayout_python": "0.30.12",
        "pdk_commit": "5e6d592e4002946a4616f798c357f0f3c06cf3b6",
    },
}

large_cluster = {
    "id": "m1_cluster_005",
    **COMMON,
    "rule_family": "offgrid_placement",
    "task_type": "clustering",
    "layout": {
        "generator": "generators.offgrid_array",
        "args": {"n": 40, "step_x_um": 15.002, "step_y_um": 15.002},
        "gds": "corpus/multi/m1_cluster_005.gds",
        "topcell": "m1_cluster_005",
    },
    "drc_expected": {"metal1_drw_Offgrid": 30720},
    "ground_truth": {
        "cause": {"type": "offgrid_array_pitch", "pitch_um": 15.002, "grid_nm": 5},
        "known_deck_discrepancy": False,
        "distinct_problems": 1,
        "root_cause": ("The 40x40 array pitch is 15.002 um, 2 nm off the 5 nm manufacturing "
                       "grid. Every off-grid instance puts its Metal1 edges off grid. "
                       "The cell itself is clean."),
        "rules_involved": ["metal1_drw_Offgrid"],
        "fix": {"type": "snap_array_pitch", "pitch_x_um": 15.0, "pitch_y_um": 15.0,
                "action": "snap the array pitch to the grid (15.0 um)",
                "layout_args": {"step_x_um": 15.0, "step_y_um": 15.0}},
    },
    "notes": "Largest clustering case: one root cause at 40x40 scale.",
}

n_sites = 1000
large_multi = {
    "id": "m1_multi_021",
    **COMMON,
    "rule_family": "metal1_spacing",
    "task_type": "root_cause",
    "layout": {
        "generator": "generators.multi_site",
        "args": {"gaps": [0.10] * n_sites, "width1s": [0.2] * n_sites},
        "gds": "corpus/multi/m1_multi_021.gds",
        "topcell": "m1_multi_021",
    },
    "drc_expected": {"M1.b": 1000, "M1.e": 1000},
    "ground_truth": {
        "cause": {"type": "spacing", "gap_um": 0.10,
                  "artifact_required_gap_um": 0.22, "spec_required_gap_um": 0.22},
        "known_deck_discrepancy": False,
        "distinct_problems": n_sites,
        "root_cause": (f"{n_sites} independent sites where a 0.2 um wire is 0.10 um from a "
                       "0.5 um wide wire over a 10 um parallel run; minimum Metal1 space is "
                       "0.18 um, and M1.e requires 0.22 um."),
        "rules_involved": ["M1.b", "M1.e"],
        "markers_per_problem": 2,
        "fix": {"type": "set_min_gap",
                "action": "increase every violating gap to at least 0.22 um",
                "artifact_value_um": 0.22, "spec_value_um": 0.22,
                "layout_args": {"gaps": [0.22] * n_sites}},
    },
    "notes": f"Largest multi-site case: {n_sites} s4 sites, 2 markers each.",
}

for t in (large_cluster, large_multi):
    t["drc"]["expected_counts"] = t.pop("drc_expected")
    t["ground_truth"]["total_markers"] = sum(t["drc"]["expected_counts"].values())
    (out_dir / f"{t['id']}.json").write_text(json.dumps(t, indent=2) + "\n")
    print("wrote", t["id"], t["drc"]["expected_counts"])
