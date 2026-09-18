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

## Signature clustering (rule + marker shape, position discarded)
| Task | markers | raw | json | proximity | signature |
|------|---------|-----|------|-----------|-----------|
| m1_multi_006 | 4 | 49,404 | 201 | 253 | 284 |
| m1_multi_020 | 400 | 89,400 | 10,101 | 11,341 | 627 |
| m1_cluster_004 | 7,680 | 905,320 | 213,512 | 213,512 | 340 |
- m1_cluster_004: 905,320 -> 340 tokens, a factor of ~2,660, by describing one repeated
  marker shape once instead of 7,680 times
- m1_multi_020: 16x smaller than compact JSON
- m1_multi_006: signature is the LARGEST compact form (284 vs 201) - with 4 markers the
  grouping structure is pure overhead. The benefit is scale-dependent, not universal.
- IMPORTANT CAVEAT: signature is lossy above 20 positions per group. On m1_cluster_004
  it keeps 20 of 7,680 positions plus an extent. It is not information-equivalent to raw
  or json, so the token comparison alone cannot decide which is better.
- What this means: whether the discarded positions matter depends on the task
  (root-cause identification vs exhaustive listing). This is exactly what the
  task-success evaluation has to determine.
