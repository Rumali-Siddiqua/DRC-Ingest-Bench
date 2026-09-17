# Phase 2 results

## Run 1: metal1.gds (IHP unit test), table metal1
- KLayout 0.30.7 (deck), klayout Python 0.30.12, tokenizer cl100k_base
- Rules violated: M1.a, M1.b, M1.e, M1.f, M1.g, M1.i
- Markers: 11
- Report: 4.8 KB, 1,736 tokens (157.8 tokens/marker, inflated by fixed header)
- Log: 27.3 KB, 11,655 tokens (~6.7x the report, no geometry)
- Header: 549 tokens (fixed); items: 1,166 tokens for 11 markers
- 106 tokens per marker, of which 37 are geometry -> 65% XML overhead per marker
- Observation: each item is 12 XML lines; only the <value> line carries geometry
- Observation: report does not state the measured value (e.g. M1.a width 0.150 vs 0.16 min)
- Caveat: one small layout, edge-pair markers only
- metal1.gds full deck: 830 rules listed, 12 with violations (~1.4% of catalogue relevant)
- Violated: M1.a/b/c/c1/d/e/f/g/i, M1Fil.a1, M1Fil.c, Cnt.h (sum = 24, matches)
- M1.c, M1.c1, M1.d not run by --table=metal1 (likely in extra rules) -> tasks must record deck options
- Cnt.h fires on the Metal1 layout -> one problem can appear under several rule tables
