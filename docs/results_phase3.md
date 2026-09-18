# Phase 3 results

## Task 3.3: M1.e investigation
Setup: KLayout 0.30.7 (PDK pins 0.30.5), full deck, --no_density, flat mode.

- M1.e real condition (code + tech JSON): space >= 0.22 um to any Metal1 wider than 0.3 um, parallel run > 1.0 um
- Report description prints half the width threshold (0.15 instead of 0.3); M1.f uses the same pattern
  -> an LLM trusting the report description is given a wrong threshold
- Injected gap between two 0.5 um wires, 10 um run:
  - gap 0.20: nothing fires (M1.e expected)
  - gap 0.10: M1.b = 1 only (M1.e expected too)
- Probe (experiments/phase3/m1e_probe.drc), same logic on both layouts:
  | Check | gap020 (5 wide wires) | IHP metal1.gds |
  |-------|-----------------------|----------------|
  | deck check (m1 sep wide) | 0 | 1 |
  | plain space 0.22 | 1 | 1 |
  | narrow sep wide | 0 | 1 |
- Observation: deck M1.e catches narrow-vs-wide, misses wide-vs-wide (likely false negative vs. rule text)
- Cause not yet confirmed; caveat: one geometry, KLayout 0.30.7 not the pinned 0.30.5
- Ground-truth policy: tasks record what the deck actually reports; deck discrepancies are noted separately
- Confirmed: gap 0.20 with wire 1 narrowed to 0.2 um -> M1.e = 1 (narrow-vs-wide fires)
- Confirmed: gap 0.20 between two 0.5 um wires -> 0 (wide-vs-wide not reported)
- Valid 3.3 tasks: gap010 (M1.b = 1), gap020_narrow (M1.e = 1)

## Task 3.6: fix check
- Fix = move wire 1 to gap 0.22 um (rule-text minimum), stored as fix.layout_args
- Validator rebuilds broken and fixed layouts from the task JSON: both tasks PASS (broken matches, fixed = 0)

## Task 3.7: site types (verified)
Each site: wide wire 0.5 um + second wire at given gap/width, 10 um parallel run,
pitch 5 x 12 um. Site types and their DRC markers:
| Site | Gap um | Width1 um | Markers | Distinct problems |
|------|--------|-----------|---------|-------------------|
| s1 | 0.10 | 0.5 | M1.b: 1 | 1 |
| s2 | 0.20 | 0.5 | none (deck miss) | 1 |
| s3 | 0.20 | 0.2 | M1.e: 1 | 1 |
| s4 | 0.10 | 0.2 | M1.b: 1, M1.e: 1 | 1 |
- all4 (one of each) = M1.b 2, M1.e 2 = exact sum -> sites are independent at this pitch
- s4 is the key clustering case: one root cause reported under two rules

## Task 3.7: task corpus
- 22 tasks generated from the verified site table (generators/make_tasks.py)
- Scales: 1 to 200 distinct problems, 1 to 400 markers; most tasks include clean distractor sites
- Validator: 22/22 PASS (expected counts match, and each stated fix clears DRC)
- Site independence holds to 200 sites; no interaction at any tested scale

## Task 3.8: clustering tasks
- Built from a clean 5-wire cell arrayed at a 15.002 um pitch (2 nm off the 5 nm grid)
- Control at 15.0 um pitch: DRC clean, so every marker comes from the pitch alone
- Measured markers: 3x3 = 160, 5x5 = 480, 10x10 = 1,920, 20x20 = 7,680 (all metal1_drw_Offgrid)
- Counts are not a simple multiple of the copy count: a 2 nm step realigns with the 5 nm grid
  every few copies, so some instances land back on grid. Counts are measured, not derived.
- Ground truth: 1 distinct problem per task; fix = snap the pitch to 15.0 um
- Largest ratio in the corpus: 7,680 markers from 1 root cause

## Phase 3 summary
- 26 tasks, all validated (rebuilt from JSON, DRC matched, fix verified clean)
- 2 single-injection, 20 multi-site (1-200 problems), 4 clustering (1 problem, up to 7,680 markers)

## Scoring schema
- Each task now carries ground_truth.problems (rules, marker_count per problem) and
  ground_truth.marker_to_problem, derived from actual DRC output via harness/add_scoring.py
- Markers are grouped by the generator site containing them (5 x 12 um pitch); clustering
  tasks group all markers under one problem (the array pitch)
- Canonical marker id: "<rule>@x0,y0,x1,y1" (3 dp), stable because DRC is deterministic
- All 26 derived problem counts match the previously stated distinct_problems
- Validator still passes 26/26 after the schema change
- Marker-to-problem ratios span 1:1 to 7,680:1
- Observation: in s4 sites the M1.b and M1.e markers share identical geometry, so one
  physical gap is reported twice under different rules
