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
