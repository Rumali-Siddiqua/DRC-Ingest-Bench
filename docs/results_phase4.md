# Phase 4 results

## Representation token costs (cl100k_base)
| Task | markers | raw | json | clustered | groups |
|------|---------|-----|------|-----------|--------|
| m1_multi_006 | 4 | 49,404 | 201 | 253 | 2 |
| m1_multi_020 | 400 | 89,400 | 10,101 | 11,341 | 200 |
| m1_cluster_004 | 7,680 | 905,320 | 215,085 | 213,512 | 3,829 |

## Negative result: proximity clustering does not reduce cost
- Grouping by geometric proximity (2 um radius) produced groups that cost MORE than the
  markers they replace: each group carries rules, count, extent and an example.
- On m1_multi_020 it grouped correctly (200 groups for 200 problems) yet was 12% larger
  than plain JSON.
- On m1_cluster_004 it failed outright: 3,829 groups for one root cause, because the
  off-grid markers sit at a 15 um pitch, far beyond any local radius.
- Interpretation: spatial proximity is the wrong primitive for a systematic fault. The
  7,680 markers share a cause because they are the same shape repeated at a regular
  pitch, not because they are near one another.
- Next candidate: cluster by signature (rule + marker size/shape, position discarded),
  which should collapse identical repeated markers regardless of where they are.
