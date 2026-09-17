# Phase 1 experiments: generic transformation tools on DRC artifacts

## markitdown 0.1.7 on a KLayout marker database
Input: experiments/phase3/run_probe_all4 report (4 markers, 830 rule categories), tokenizer cl100k_base.

| Input | Raw tokens | markitdown tokens | Change |
|-------|------------|-------------------|--------|
| .lyrdb | 49,392 | 49,392 | 0% |
| same file renamed .xml | 49,392 | 49,392 | 0% |

- markitdown returns the XML unchanged; it has no converter for this format and no error is raised
- Renaming to .xml changes nothing, so the file extension is not the barrier
- Geometry survives only because nothing was transformed
- Neither waste mode is addressed: the 830-rule catalogue and the per-marker XML both remain
- Conclusion: for DRC marker databases, generic document-to-LLM conversion is inert, not merely domain-blind

## TOON and JSON vs raw XML (same violations, cl100k_base)
| Report | Raw XML | JSON | TOON | TOON vs JSON |
|--------|---------|------|------|--------------|
| 4 markers | 49,392 | 177 (0.4%) | 161 (0.3%) | 9.0% |
| 7,680 markers | 897,638 | 418,565 (46.6%) | 372,494 (41.5%) | 11.0% |
- Records extracted as {rule, cell, geometry}; JSON is compact-separator json.dumps
- Most of the saving is structuring (XML -> JSON), not serialization (JSON -> TOON)
- Small report: the 830-rule catalogue disappears once only fired rules are kept
- TOON gives 9-11% here vs the 42.6% reported on its own benchmarks: our rows have
  3 short field names and one long quoted geometry string, so little syntax remains to compress
- Off-grid geometry is degenerate (same point repeated, ~48 tok/marker) -> semantic
  restructuring, not syntactic compression, is where the remaining cost lies
