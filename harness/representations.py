"""Turn a DRC report into each candidate representation for the benchmark.

raw       - the .lyrdb file verbatim (baseline)
json      - fired rules only, as compact records
clustered - markers grouped by geometric proximity, with counts and one example each

The clusterer must never consult ground truth: its own accuracy is a measurable
property, and using the answer to build the question would invalidate the comparison.
"""
import json
import re
from pathlib import Path

import klayout.rdb as rdb

NUM = re.compile(r"-?\d+\.?\d*")
CLUSTER_RADIUS_UM = 2.0   # below half the 5 um site pitch; independent of ground truth


def read_markers(report):
    """[(rule, rule_description, bbox)] for every marker in the report."""
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
                out.append((cat.name(), cat.description,
                            (min(xs), min(ys), max(xs), max(ys))))
    return out


def raw(report):
    return Path(report).read_text(encoding="utf-8")


def compact_json(report):
    ms = read_markers(report)
    rules = {}
    for rule, desc, _ in ms:
        rules.setdefault(rule, desc)
    violations = [{"rule": r, "bbox": [round(c, 3) for c in bb]} for r, _, bb in ms]
    return json.dumps({"rules": rules, "violations": violations}, separators=(",", ":"))


def _centre(bb):
    return ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)


def clustered(report):
    """Group markers whose centres lie within CLUSTER_RADIUS_UM of a cluster's first member."""
    ms = read_markers(report)
    rules = {}
    clusters = []   # [(seed_centre, [(rule, bbox), ...])]

    for rule, desc, bb in ms:
        rules.setdefault(rule, desc)
        c = _centre(bb)
        for seed, members in clusters:
            if abs(c[0] - seed[0]) <= CLUSTER_RADIUS_UM and abs(c[1] - seed[1]) <= CLUSTER_RADIUS_UM:
                members.append((rule, bb))
                break
        else:
            clusters.append((c, [(rule, bb)]))

    groups = []
    for i, (_, members) in enumerate(clusters, 1):
        xs0 = min(b[0] for _, b in members)
        ys0 = min(b[1] for _, b in members)
        xs1 = max(b[2] for _, b in members)
        ys1 = max(b[3] for _, b in members)
        groups.append({
            "group": i,
            "rules": sorted({r for r, _ in members}),
            "marker_count": len(members),
            "extent": [round(v, 3) for v in (xs0, ys0, xs1, ys1)],
            "example": [round(v, 3) for v in members[0][1]],
        })

    return json.dumps({
        "rules": rules,
        "total_markers": len(ms),
        "group_count": len(groups),
        "groups": groups,
        "note": ("Markers are grouped by geometric proximity, not by verified root cause. "
                 "A group may hold several problems, or one problem may span several groups."),
    }, separators=(",", ":"))


BUILDERS = {"raw": raw, "json": compact_json, "clustered": clustered}


def build(name, report):
    return BUILDERS[name](report)
