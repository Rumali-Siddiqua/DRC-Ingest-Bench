# Answer format and scoring contract

Every model, under every representation, returns one JSON object in this form.
Nothing else is scored, so the prompt must request exactly this.

```json
{
  "problems": [
    {
      "id": 1,
      "rules": ["M1.b", "M1.e"],
      "location_um": [0.55, 5.0],
      "marker_count": 2,
      "root_cause": "wire 1 is 0.10 um from wire 0; minimum Metal1 space is 0.18 um",
      "fix_min_gap_um": 0.22
    }
  ]
}
```

## Fields

| Field | Required | Meaning |
|-------|----------|---------|
| `id` | yes | Any integer, unique within the answer. Not compared to ground truth. |
| `rules` | yes | Rule names this problem produces markers under. |
| `location_um` | yes | A point inside the problem, in micrometres. |
| `marker_count` | no | How many markers the model attributes to this problem. |
| `root_cause` | no | Free text; not scored automatically in the pilot. |
| `fix_min_gap_um` | no | Minimum gap the model proposes. |

## Location matching

A reported problem matches a ground-truth problem when its `location_um` falls
within **1.0 um** of the ground-truth problem's marker bounding boxes.

Rationale: generator sites are on a 5 x 12 um pitch, so 1.0 um (one fifth of the
smaller pitch) cannot reach a neighbouring site, while not demanding precision the
representation may not carry. Each ground-truth problem is matched at most once,
nearest first.

Coordinates rather than marker identifiers are used because the interface-access
strategy never shows the model full marker text, and cross-strategy comparability
is the purpose of the benchmark.

## Metrics

| Metric | Definition |
|--------|------------|
| Problem-count error | reported problems - ground-truth problems |
| Precision | matched reported problems / reported problems |
| Recall | matched ground-truth problems / ground-truth problems |
| F1 | harmonic mean of precision and recall |
| Rule accuracy | matched problems whose `rules` set equals ground truth |
| Fix validity | matched problems whose `fix_min_gap_um` >= the required gap |

Reported alongside: input tokens, output tokens, cost, latency, model and version,
representation, and task id.

## Malformed answers

An answer that is not valid JSON, or lacks `problems`, scores zero on every metric
and is recorded as a parse failure. Parse-failure rate is reported per
representation, since a representation that confuses models is a finding.

## Structured cause (added after the pilot audit)

Each problem may carry a machine-checkable `cause` alongside the prose `root_cause`:

```json
"cause": {"type": "spacing", "gap_um": 0.10, "required_gap_um": 0.18}
"cause": {"type": "offgrid_array_pitch", "pitch_um": 15.002}
```

`cause_accuracy` is the share of matched problems whose cause type and values match ground
truth. It is null when a task's cause type has no automated check.

## Fixes are typed

| Type | Model returns | Tasks |
|------|---------------|-------|
| `set_min_gap` | `fix_min_gap_um` | 23 |
| `snap_array_pitch` | `fix_pitch_um: [x, y]` | 5 |

`fix_validity` is null, not zero, when a task's fix type has no
python - << 'PY'
from pathlib import Path

# mock_perfect: use the artifact value and emit a structured cause.
p = Path("harness/run.py")
t = p.read_text()
old = """        if gt["fix"].get("type") == "snap_array_pitch":
            entry["fix_pitch_um"] = [gt["fix"]["pitch_x_um"], gt["fix"]["pitch_y_um"]]
        else:
            entry["fix_min_gap_um"] = gt["fix"].get("min_gap_um")
        probs.append(entry)"""
new = """        cause = gt.get("cause", {})
        if gt["fix"].get("type") == "snap_array_pitch":
            entry["fix_pitch_um"] = [gt["fix"]["pitch_x_um"], gt["fix"]["pitch_y_um"]]
            entry["cause"] = {"type": "offgrid_array_pitch", "pitch_um": cause.get("pitch_um")}
        else:
            entry["fix_min_gap_um"] = gt["fix"].get("artifact_value_um")
            entry["cause"] = {"type": "spacing", "gap_um": cause.get("gap_um"),
                              "required_gap_um": cause.get("artifact_required_gap_um")}
        probs.append(entry)"""
assert old in t, "mock_perfect block not found"
p.write_text(t.replace(old, new))
print("mock_perfect updated")
PY

cat >> docs/answer_format.md << 'EOF'

## Structured cause (added after the pilot audit)

Each problem may carry a machine-checkable `cause` alongside the prose `root_cause`:

```json
"cause": {"type": "spacing", "gap_um": 0.10, "required_gap_um": 0.18}
"cause": {"type": "offgrid_array_pitch", "pitch_um": 15.002}
```

`cause_accuracy` is the share of matched problems whose cause type and values match ground
truth. It is null when a task's cause type has no automated check.

## Fixes are typed

| Type | Model returns | Tasks |
|------|---------------|-------|
| `set_min_gap` | `fix_min_gap_um` | 23 |
| `snap_array_pitch` | `fix_pitch_um: [x, y]` | 5 |

`fix_validity` is null, not zero, when a task's fix type has no automated check. Zero means
the model proposed an invalid fix.

## Artifact-conditioned scoring

Fix and cause scoring use the constraint **observable in the artifact the model was given**,
not the intended rule semantics. Where the two differ, both are recorded:

```json
"cause": {"artifact_required_gap_um": 0.18, "spec_required_gap_um": 0.22}
"known_deck_discrepancy": true
```

This affects 7 spacing tasks, where two wide wires produce an M1.b marker (0.18 um) although
the M1.e rule text would require 0.22 um; the deck does not report M1.e for wide-vs-wide
geometry (see docs/results_phase3.md). A model reading such a report cannot know about a rule
the report never mentions, so scoring it against 0.22 would test hidden knowledge rather than
artifact-ingestion quality. Results can be broken out by `known_deck_discrepancy`, and a
secondary spec-conditioned metric can be reported later if models are given rule-text access.
