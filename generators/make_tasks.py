"""Generate benchmark task JSON files from verified site types (see docs/results_phase3.md)."""
import json
from pathlib import Path

# gap, width1, markers produced by one site
SITES = {
    "s1": (0.10, 0.5, {"M1.b": 1}),
    "s3": (0.20, 0.2, {"M1.e": 1}),
    "s4": (0.10, 0.2, {"M1.b": 1, "M1.e": 1}),
}
CLEAN = (0.30, 0.5, {})   # a site with no violation, used as filler

# (task number, site type, violating sites, clean sites)
PLAN = [(i + 1, s, v, c) for i, (s, v, c) in enumerate([
    ("s1", 1, 0), ("s3", 1, 0), ("s4", 1, 0),
    ("s1", 2, 2), ("s3", 2, 2), ("s4", 2, 2),
    ("s1", 5, 5), ("s3", 5, 5), ("s4", 5, 5),
    ("s1", 10, 10), ("s3", 10, 10), ("s4", 10, 10),
    ("s1", 25, 25), ("s3", 25, 25), ("s4", 25, 25),
    ("s1", 50, 50), ("s3", 50, 50), ("s4", 50, 50),
    ("s4", 100, 100), ("s4", 200, 200),
])]

RULE_TEXT = {
    "M1.b": "minimum Metal1 space is 0.18 um",
    "M1.e": "minimum space to a wire wider than 0.3 um with parallel run > 1.0 um is 0.22 um",
}

out_dir = Path("corpus/tasks")
out_dir.mkdir(parents=True, exist_ok=True)

for n, site, n_viol, n_clean in PLAN:
    gap, w1, markers = SITES[site]
    task_id = f"m1_multi_{n:03d}"
    expected = {rule: count * n_viol for rule, count in markers.items()}
    rules = sorted(markers)
    task = {
        "id": task_id,
        "version": 1,
        "rule_family": "metal1_spacing",
        "site_type": site,
        "layout": {
            "generator": "generators.multi_site",
            "args": {
                "gaps": [gap] * n_viol + [CLEAN[0]] * n_clean,
                "width1s": [w1] * n_viol + [CLEAN[1]] * n_clean,
            },
            "gds": f"corpus/multi/{task_id}.gds",
            "topcell": task_id,
        },
        "drc": {
            "deck": "IHP-Open-PDK sg13g2 KLayout (run_drc.py)",
            "options": ["--no_density", "--run_mode=flat"],
        "klayout_version": "0.30.7",
        "klayout_python": "0.30.12",
        "pdk_commit": "5e6d592e4002946a4616f798c357f0f3c06cf3b6",
            "expected_counts": expected,
        },
        "ground_truth": {
            "cause": {"type": "spacing", "gap_um": gap,
                      "artifact_required_gap_um": 0.22 if "M1.e" in expected else 0.18,
                      "spec_required_gap_um": 0.22},
            "known_deck_discrepancy": "M1.e" not in expected,
            "distinct_problems": n_viol,
            "total_markers": sum(expected.values()),
            "root_cause": (f"{n_viol} independent site(s) where a second wire is {gap} um "
                           f"from a 0.5 um wide wire over a 10 um parallel run; "
                           + "; ".join(RULE_TEXT[r] for r in rules) + "."),
            "rules_involved": rules,
            "markers_per_problem": sum(markers.values()),
            "clean_sites": n_clean,
            "fix": {
                "type": "set_min_gap",
                "action": "increase every violating gap to at least 0.22 um",
                "artifact_value_um": 0.22 if "M1.e" in expected else 0.18,
                "spec_value_um": 0.22,
                "layout_args": {"gaps": [0.22] * n_viol + [CLEAN[0]] * n_clean},
            },
        },
        "notes": (f"Site type {site}. Verified in docs/results_phase3.md. "
                  f"{n_clean} clean site(s) act as distractors."),
    }
    (out_dir / f"{task_id}.json").write_text(json.dumps(task, indent=2) + "\n")

print(f"Wrote {len(PLAN)} task files to {out_dir}")
