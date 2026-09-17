# Phase 2 results

Setup: KLayout 0.30.7 (deck), klayout Python 0.30.12, tokenizer cl100k_base,
IHP SG13G2 unit test layouts.

## Run 1: metal1.gds, table metal1 only
- Rules violated: M1.a, M1.b, M1.e, M1.f, M1.g, M1.i
- Markers: 11
- Report: 4.8 KB, 1,736 tokens (157.8 tokens/marker, inflated by fixed header)
- Log: 27.3 KB, 11,655 tokens (~6.7x the report, no geometry)
- Header: 549 tokens (fixed); items: 1,166 tokens for 11 markers
- 106 tokens per marker, of which 37 are geometry -> 65% XML overhead per marker
- Observation: each item is 12 XML lines; only the <value> line carries geometry
- Observation: report does not state the measured value (e.g. M1.a width 0.150 vs 0.16 min)
- Caveat: one small layout, edge-pair markers only

## Run 2: full deck (--no_density) on 5 unit layouts
| Layout | Markers | Header tok | Item tok | Header share |
|--------|---------|------------|----------|--------------|
| metal1 | 24 | 48,986 | 2,546 | 95% |
| via2 | 35 | 48,986 | 3,963 | 93% |
| cont | 63 | 48,984 | 6,787 | 88% |
| nwell | 97 | 48,984 | 10,291 | 83% |
| gatpoly | 98 | 48,988 | 10,705 | 82% |
- Per-marker overhead stable at 62-66% across all 5 rule families
- Full-deck header ~49k tokens: report lists all rules, including those with 0 violations
- metal1.gds: 830 rules listed, 12 with violations (~1.4% of catalogue relevant)
- Violated: M1.a/b/c/c1/d/e/f/g/i, M1Fil.a1, M1Fil.c, Cnt.h (sum = 24, matches)
- M1.c, M1.c1, M1.d not run by --table=metal1 -> tasks must record deck options
- Cnt.h fires on the Metal1 layout -> one problem can appear under several rule tables
- Two kinds of waste: fixed rule catalogue (small reports), per-marker XML (large reports)

## Run 3 (invalid, kept as a lesson): scaled arrays with 1.2x step
- 1.2x cell-size step put most copies off grid; counts 12x expected (4,644 vs 384 for 4x4)
- 4x4 = 384 real markers + 4,260 Offgrid markers (6 layers, each divisible by 15 off-grid copies)
- Fixed by snapping the step to whole microns
- Kept as generators/array_layout_offgrid.py: one root cause -> thousands of markers (clustering task candidate)
- Lesson: every generated task must be DRC-validated against its expected count

## Run 4 (valid): scaled metal1 arrays, step 53 x 118 um, full deck, flat mode
| Grid | Markers | Header tok | Item tok | Total tok | Header share | Item overhead |
|------|---------|------------|----------|-----------|--------------|---------------|
| 4x4 | 384 | 48,992 | 41,852 | 90,844 | 54% | 67% |
| 10x10 | 2,400 | 48,992 | 262,050 | 311,042 | 16% | 66% |
| 20x20 | 9,600 | 48,992 | 1,067,980 | 1,116,972 | 4% | 65% |
| 40x40 | 38,400 | 48,992 | 4,381,560 | 4,430,552 | 1% | 64% |
- All counts match 24 x N^2 (DRC-validated)
- Cost linear in markers (~110 tok/marker); rises 109 -> 114 as coordinates grow
- 38,400 markers = 24 distinct problems x 1,600 identical cells; raw = 4.4M tokens
- DRC runtime 11s -> 42s; reading the report costs far more than producing it
