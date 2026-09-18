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
| m1_cluster_004 | 7,680 | 905,320 | 215,085 | 213,512 | 340 |
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

## Context fit and per-task costs (all 26 tasks, cl100k_base)
Full table: experiments/phase4/context_fit.csv

Tasks fitting a window (representation alone, excluding prompt and answer):
| window | raw | json | clustered | signature |
|--------|-----|------|-----------|-----------|
| 128k | 24/26 | 25/26 | 25/26 | 26/26 |
| 200k | 24/26 | 25/26 | 25/26 | 26/26 |
| 1M | 26/26 | 26/26 | 26/26 | 26/26 |
- Weak result: the corpus does not reach the scale where raw ingestion is impossible.
  The Phase 2 40x40 case (4.47M tokens) exceeds every window but is not a task.
  Adding a task at that scale would make this a real finding.

Stronger observations from the per-task table:
- Raw carries a fixed ~49,000-token floor: m1_space_001 costs 49,101 tokens raw vs 66
  as JSON for a single violation (744x), entirely the rule catalogue.
- Signature cost is nearly flat across scale: 151 tokens at 1 marker, 340 at 7,680,
  because it scales with distinct marker shapes, not marker count. JSON scales linearly.
- Signature loses on small tasks (151 vs 66 at 1 marker): grouping structure is overhead
  when there is nothing to collapse.
- Signature gains least on 2:1 tasks (m1_multi_015: 627 vs 1,351, only 2x), where two
  shapes and 50 distinct positions leave little to compress.


## Corpus extended to 28 tasks; context fit becomes decisive
Added m1_cluster_005 (40x40 off-grid array, 30,720 markers, 1 root cause) and
m1_multi_021 (1,000 s4 sites, 2,000 markers, 1,000 problems). Both DRC-validated; 28/28 pass.

| Task | markers | problems | raw | json | clustered | signature |
|------|---------|----------|-----|------|-----------|-----------|
| m1_cluster_005 | 30,720 | 1 | 3,481,960 | 860,205 | 856,168 | 340 |
| m1_multi_021 | 2,000 | 1,000 | 252,320 | 50,761 | 56,804 | 676 |

Tasks fitting a window (representation alone):
| window | raw | json | clustered | signature |
|--------|-----|------|-----------|-----------|
| 128k | 24/28 | 26/28 | 26/28 | 28/28 |
| 200k | 24/28 | 26/28 | 26/28 | 28/28 |
| 1M | 27/28 | 28/28 | 28/28 | 28/28 |

- m1_cluster_005 raw (3.48M tokens) exceeds every window listed. Compact JSON (860k)
  also exceeds 128k and 200k, so structuring alone does not rescue it at this scale.
  Signature answers in 340 tokens: a factor of 10,241 against raw.
- This refines the earlier finding, for representation SIZE only: semantic restructuring
  can outperform syntactic compression when the dominant redundancy is semantic rather than
  syntactic. Whether that reduction preserves or improves debugging success is untested.
- m1_multi_021 is the sharpest test in the corpus: 676 tokens describing 1,000 genuinely
  distinct problems, with only 20 of 1,000 positions shown. Whether a model can report
  them correctly from that is precisely what the task-success evaluation must decide.

## Harness baselines (mock models, no API cost)
Three reference strategies establish the scale that real model results are read against:

| Strategy | 1:1 tasks | 2:1 tasks (s4) | clustering tasks |
|----------|-----------|----------------|------------------|
| mock_perfect (answers from ground truth) | 1.00 | 1.00 | 1.00 |
| mock_one_per_marker (every marker a problem) | 1.00 | 0.67 | 0.00 |
| mock_empty | 0.00 | 0.00 | 0.00 |

- mock_perfect scoring 1.00 on all 112 runs confirms the scorer and the ground truth agree.
- mock_one_per_marker is the discriminating case: marker-counting is a perfect strategy on
  the 1:1 tasks and worthless on the clustering tasks (f1 = 0.00 at 480 markers and above).
  A corpus of only 1:1 tasks could not distinguish counting from reasoning.
- The 0.67 on s4 tasks is precision 0.5, recall 1.0: one physical gap reported twice.
- mock_empty scores 0.00 on all 112 runs, as the floor should.
- CAVEAT: mock models answer from ground truth, not from the payload, so their scores are
  identical across all four representations. These runs validate the scorer, not the
  representations, and mock_perfect is NOT an achievable ceiling for lossy representations
  (signature shows only 20 of 1,000 positions on m1_multi_021).

## Correction: typed fixes
- The original scorer only understood a min_gap_um fix, so the 5 clustering tasks scored
  fix_validity = 0 even for a correct answer. Zero implied a wrong fix; the metric simply
  did not apply.
- Fixes are now typed: set_min_gap (23 tasks) and snap_array_pitch (5 tasks). The scorer
  handles each, and fix_validity is null when a task's fix type has no automated check.
- The earlier note that mock_perfect scoring 1.00 "confirms the scorer and ground truth
  agree" referred to f1 only. With typed fixes, mock_perfect now scores 1.00 on f1,
  rule accuracy and fix validity across all 112 runs.

## Artifact-conditioned scoring (after the pilot audit)
- Fixes are typed: set_min_gap (23 tasks), snap_array_pitch (5). fix_validity is null, not
  zero, where a task's fix type has no automated check.
- Each task carries a structured cause (spacing, or offgrid_array_pitch) alongside the prose,
  giving a deterministic cause_accuracy without an LLM judge.
- Spacing tasks record artifact_required_gap_um and spec_required_gap_um separately. On the
  7 wide-vs-wide tasks the deck reports only M1.b (0.18 um) although the M1.e rule text
  requires 0.22 um; those tasks carry known_deck_discrepancy = true.
- Policy: primary scoring is artifact-conditioned. A model is judged on the constraints
  observable in the report it was given, since penalising it for an unreported rule would
  test hidden knowledge rather than artifact ingestion. Results can be broken out by
  known_deck_discrepancy.
- mock_perfect now scores 1.00 on f1, fix validity and cause accuracy across all 112 runs.
- Scorer performance: candidate pairs are pre-filtered by problem extent, avoiding the
  1,000 x 1,000 distance comparisons that made m1_multi_021 impractically slow.
