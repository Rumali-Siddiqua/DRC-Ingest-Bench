"""Run tasks through a representation and a model, score the answers, log the metrics.

The model is a function: (prompt, task) -> (answer_text, input_tokens, output_tokens).
MOCK_MODELS need no API and cost nothing; they exist to test the pipeline and to give
trivial baselines any real model must beat.
"""
import csv
import glob
import json
import re
import time
from pathlib import Path

import tiktoken

from harness.representations import build
from harness.score import score

enc = tiktoken.get_encoding("cl100k_base")

PROMPT = """You are debugging a DRC (design rule check) result from the IHP SG13G2 process.

Below is the verification output in the "{rep}" representation.

Identify the DISTINCT PHYSICAL PROBLEMS in the layout. Several markers, possibly under
different rules, can come from one physical problem; report that as ONE problem.

Reply with ONE JSON object and nothing else:
{{"problems": [{{"id": 1, "rules": ["<rule names>"], "location_um": [x, y],
  "marker_count": <int>, "root_cause": "<one sentence>", "fix_min_gap_um": <number>}}]}}

location_um is any point inside the problem, in micrometres.

--- verification output ---
{payload}
--- end ---"""


def make_prompt(task, rep_name, payload):
    return PROMPT.format(rep=rep_name, payload=payload)


def parse_answer(text):
    """Pull the first JSON object out of a reply; tolerate code fences and stray prose."""
    text = re.sub(r"```(?:json)?|```", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        depth += ch == "{"
        depth -= ch == "}"
        if depth == 0:
            try:
                return json.loads(text[start:i + 1])
            except json.JSONDecodeError:
                return None
    return None


# --- free baseline "models" -------------------------------------------------

def mock_perfect(prompt, task):
    """Upper bound: answers from ground truth. Any real model should score at or below this."""
    gt = task["ground_truth"]
    probs = []
    for i, (pid, info) in enumerate(gt["problems"].items(), 1):
        boxes = [k for k, v in gt["marker_to_problem"].items() if v == pid]
        m = re.search(r"@([-\d.]+),([-\d.]+),([-\d.]+),([-\d.]+)$", boxes[0])
        x = (float(m[1]) + float(m[3])) / 2
        y = (float(m[2]) + float(m[4])) / 2
        probs.append({"id": i, "rules": info["rules"], "location_um": [x, y],
                      "marker_count": info["marker_count"],
                      "fix_min_gap_um": gt["fix"].get("min_gap_um")})
    text = json.dumps({"problems": probs})
    return text, len(enc.encode(prompt)), len(enc.encode(text))


def mock_one_per_marker(prompt, task):
    """The failure mode this benchmark exists to detect: every marker read as a problem."""
    gt = task["ground_truth"]
    probs = []
    for i, mid in enumerate(gt["marker_to_problem"], 1):
        m = re.search(r"^(.+)@([-\d.]+),([-\d.]+),([-\d.]+),([-\d.]+)$", mid)
        x = (float(m[2]) + float(m[4])) / 2
        y = (float(m[3]) + float(m[5])) / 2
        probs.append({"id": i, "rules": [m[1]], "location_um": [x, y], "marker_count": 1})
    text = json.dumps({"problems": probs})
    return text, len(enc.encode(prompt)), len(enc.encode(text))


def mock_empty(prompt, task):
    """Floor: reports nothing."""
    text = '{"problems": []}'
    return text, len(enc.encode(prompt)), len(enc.encode(text))


MOCK_MODELS = {"mock_perfect": mock_perfect,
               "mock_one_per_marker": mock_one_per_marker,
               "mock_empty": mock_empty}


# --- runner -----------------------------------------------------------------

def report_for(task_id):
    found = glob.glob(f"experiments/validate/{task_id}/broken/*.lyrdb")
    return found[0] if found else None


def run(task_paths, rep_names, model_name, model_fn, out_csv, cost_per_mtok=(0.0, 0.0)):
    rows = []
    for tp in task_paths:
        task = json.loads(Path(tp).read_text())
        report = report_for(task["id"])
        if not report:
            print(f"skip {task['id']}: no report")
            continue
        for rep in rep_names:
            payload = build(rep, report)
            prompt = make_prompt(task, rep, payload)
            t0 = time.time()
            text, tin, tout = model_fn(prompt, task)
            latency = time.time() - t0
            s = score(task, parse_answer(text))
            cost = tin / 1e6 * cost_per_mtok[0] + tout / 1e6 * cost_per_mtok[1]
            rows.append({"task": task["id"], "representation": rep, "model": model_name,
                         "input_tokens": tin, "output_tokens": tout,
                         "cost_usd": round(cost, 6), "latency_s": round(latency, 3), **s})
            print(f"{task['id']:18s} {rep:10s} {model_name:20s} "
                  f"in={tin:>9,d} f1={s['f1']:.2f} matched={s.get('matched', 0)}/{s['truth']}")

    out = Path(out_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {out} ({len(rows)} runs)")
    return rows


if __name__ == "__main__":
    import sys
    model = sys.argv[1] if len(sys.argv) > 1 else "mock_perfect"
    tasks = sorted(Path("corpus/tasks").glob("*.json"))
    run(tasks, ["raw", "json", "clustered", "signature"], model, MOCK_MODELS[model],
        f"experiments/phase4/runs_{model}.csv")
