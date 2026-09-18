"""Token cost of each representation, per task."""
import glob
import json as _json
import sys

import tiktoken

from harness.representations import build

enc = tiktoken.get_encoding("cl100k_base")
print(f"{'task':22s} {'raw':>10s} {'json':>9s} {'clustered':>10s} {'signature':>10s} {'groups':>7s}")
for task_id in sys.argv[1:]:
    rep = glob.glob(f"experiments/validate/{task_id}/broken/*.lyrdb")
    if not rep:
        print(f"{task_id:22s} (no report - run the validator first)")
        continue
    sizes = {k: len(enc.encode(build(k, rep[0]))) for k in ("raw", "json", "clustered", "signature")}
    groups = _json.loads(build("clustered", rep[0]))["group_count"]
    print(f"{task_id:22s} {sizes['raw']:10,d} {sizes['json']:9,d} {sizes['clustered']:10,d} {sizes['signature']:10,d} {groups:7d}")
