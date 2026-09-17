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
