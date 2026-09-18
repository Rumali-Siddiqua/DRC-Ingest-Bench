# Rebuilding the corpus from scratch

The corpus is produced in stages. Task definitions are generated; ground-truth mappings are
derived from actual DRC output. Both are required, in this order.

Prerequisites: the environment in `docs/environment.md`, especially the PDK commit and the
KLayout versions. Different versions may report different markers.

## 1. Generate task definitions (28 tasks)

    python -m generators.make_space_tasks     # 2 single-injection
    python -m generators.make_tasks           # 20 multi-site
    python -m generators.make_cluster_tasks   # 4 clustering
    python -m generators.make_large_tasks     # 2 large-scale

Each task carries its layout recipe, deck options, tool versions, expected DRC counts,
structured cause, and typed fix. Expected counts are measured values baked into the
generators; they are not predicted.

## 2. Validate against DRC

    python -m harness.validate

Rebuilds every layout from its JSON, runs DRC, requires an exact match with
`expected_counts`, then applies the stated fix and requires a clean run. Expect 28/28.

## 3. Derive the scoring ground truth

    python -m harness.add_scoring

Adds `ground_truth.problems` and `ground_truth.marker_to_problem` by grouping the markers
DRC actually produced. These cannot be generated without a DRC run, which is why they are a
separate stage. Expect 28/28 consistent: each derived problem count must match the
`distinct_problems` the generator declared.

## 4. Validate again

    python -m harness.validate
    python -m pytest tests/ -q

## 5. Representation and harness experiments

    python experiments/phase4/context_fit.py
    python -m harness.run mock_perfect
    python -m harness.run mock_one_per_marker
    python -m harness.run mock_empty

## Verifying a rebuild

Regenerating into a scratch copy reproduces every committed field except `problems` and
`marker_to_problem`, which stage 3 adds:

    rm -rf /tmp/regen && mkdir -p /tmp/regen
    cp -r generators harness corpus /tmp/regen/
    cd /tmp/regen && rm -f corpus/tasks/*.json
    python -m generators.make_space_tasks && python -m generators.make_tasks
    python -m generators.make_cluster_tasks && python -m generators.make_large_tasks
