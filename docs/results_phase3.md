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
