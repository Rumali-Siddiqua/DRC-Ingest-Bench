"""For every task and representation: token cost, and whether it fits a context window."""
import csv
import glob
import json
from pathlib import Path

import tiktoken

from harness.representations import build

enc = tiktoken.get_encoding("cl100k_base")
REPS = ("raw", "json", "clustered", "signature")
# Illustrative window sizes; the prompt and the answer also need room.
WINDOWS = {"128k": 128_000, "200k": 200_000, "1M": 1_000_000}

rows = []
for task_path in sorted(Path("corpus/tasks").glob("*.json")):
    task = json.loads(task_path.read_text())
    found = glob.glob(f"experiments/validate/{task['id']}/broken/*.lyrdb")
    if not found:
        print(f"skip {task['id']}: no report (run the validator first)")
        continue
    gt = task["ground_truth"]
    row = {"task": task["id"],
           "markers": sum(task["drc"]["expected_counts"].values()),
           "problems": gt["distinct_problems"]}
    for rep in REPS:
        row[rep] = len(enc.encode(build(rep, found[0])))
    rows.append(row)

out = Path("experiments/phase4/context_fit.csv")
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["task", "markers", "problems", *REPS])
    w.writeheader()
    w.writerows(rows)

print(f"{'task':22s} {'markers':>8s} {'probs':>6s} " + " ".join(f"{r:>10s}" for r in REPS))
for r in rows:
    print(f"{r['task']:22s} {r['markers']:8,d} {r['problems']:6d} " +
          " ".join(f"{r[rep]:10,d}" for rep in REPS))

print("\nTasks that fit, by window and representation:")
print(f"{'window':8s} " + " ".join(f"{r:>12s}" for r in REPS))
for name, limit in WINDOWS.items():
    counts = [sum(1 for r in rows if r[rep] <= limit) for rep in REPS]
    print(f"{name:8s} " + " ".join(f"{c:>9d}/{len(rows)}" for c in counts))

print(f"\nWrote {out}")
