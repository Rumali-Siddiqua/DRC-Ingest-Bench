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
