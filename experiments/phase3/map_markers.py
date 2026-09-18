"""Assign each marker in a report to the generator site that produced it."""
import re
import sys

import klayout.rdb as rdb

PITCH_X, PITCH_Y = 5.0, 12.0   # from generators/multi_site.py
NUM = re.compile(r"-?\d+\.?\d*")


def marker_bbox(value_str):
    n = [float(x) for x in NUM.findall(value_str)]
    xs, ys = n[0::2], n[1::2]
    return min(xs), min(ys), max(xs), max(ys)


def site_of(x0, y0):
    return int(y0 // PITCH_Y), int(x0 // PITCH_X)   # (row, col)


db = rdb.ReportDatabase("")
db.load(sys.argv[1])

rows = []
for cat in db.each_category():
    if not cat.num_items():
        continue
    for item in db.each_item_per_category(cat.rdb_id()):
        for v in item.each_value():
            bb = marker_bbox(v.to_s())
            r, c = site_of(bb[0], bb[1])
            rows.append((cat.name(), r, c, bb))

print(f"{'rule':22s} {'site':10s} bbox")
for rule, r, c, bb in sorted(rows, key=lambda t: (t[1], t[2], t[0])):
    print(f"{rule:22s} ({r},{c}){'':4s} ({bb[0]:.3f},{bb[1]:.3f})-({bb[2]:.3f},{bb[3]:.3f})")

sites = {(r, c) for _, r, c, _ in rows}
print(f"\nmarkers: {len(rows)}   distinct sites: {len(sites)}")
