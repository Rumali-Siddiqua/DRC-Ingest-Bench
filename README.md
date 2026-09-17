# drc-ingest-bench

**A benchmark for measuring how well LLM agents can read and debug DRC (Design Rule Check) results.**

> Status: early development (Phase 1 pilot). Interfaces, formats, and results will change.

---

## The problem

DRC outputs were designed for humans and GUIs, not for language models. A marker database can hold
thousands of near-identical geometry entries, engine logs are unstructured text, and layouts are binary
GDS that an LLM cannot read at all. As LLM agents enter EDA flows, they consume these artifacts as-is,
spending context window on syntax and repetition instead of on the information that matters.

Nobody has measured what this costs, or tested what a better representation should look like.
This project builds that measurement.

## Research questions

1. What benchmark of ground-truth DRC debugging tasks can measure how well an agent ingests
   verification artifacts, separating format effects from model effects?
2. Which strategy gives the best task success per token?
   - **Syntactic compression:** same information, fewer tokens
   - **Semantic restructuring:** clustering by root cause, summary first, drill-down on demand
   - **Interface access:** no file ingestion; the agent queries a violation database through tools
3. What textual form of the geometry around a violation best supports root-cause reasoning?
4. Can agents generate parsers for unknown report formats reliably, when gated by deterministic validation?

The **raw artifact is always the baseline**, and every result is reported as task success versus
token budget and cost, across more than one model.

## Current scope (Phase 1)

This phase uses public resources only:

- IHP SG13G2 KLayout DRC deck and regression layouts from the [IHP Open PDK](https://github.com/IHP-GmbH/IHP-Open-PDK)
- Violation-injected synthetic layouts, where the root cause is known by construction
- One rule family, 20 to 50 tasks, the harness running end to end

## Roadmap

| Phase | Goal | Status |
|-------|------|--------|
| 0 | Repository setup | Done |
| 1 | Survey of agentic EDA, token-efficient formats, tool interfaces | Planned |
| 2 | Token and cost measurement of raw KLayout marker databases | Done |
| 3 | Benchmark pilot: violation injection and ground-truth tasks | Planned |
| 4 | Evaluation harness: raw baseline vs. one transformed candidate, two models | Planned |
| 5 | Write-up of pilot results | Planned |

Detailed progress is tracked in [TRACKER.md](TRACKER.md).

## Repository layout

```
docs/          survey, design notes, results
corpus/        layouts, decks, ground-truth task files
generators/    violation-injection scripts
transforms/    raw artifacts -> candidate representations
harness/       task runner, scoring, cost and latency logging
experiments/   run configurations and results
tests/         unit and validation tests
```

## Getting started

> Setup instructions will be completed once Phase 2 tooling is in place.

Requirements (planned):

- Python 3.10+
- [KLayout](https://www.klayout.de) and the `klayout` Python package
- IHP Open PDK (SG13G2)

```bash
git clone <repo-url>
cd drc-ingest-bench
pip install -e ".[dev]"
pytest
```

## Task types

| Task | What the agent must do | Scored by |
|------|------------------------|-----------|
| Root-cause identification | Explain why a set of violations exists | Match against ground-truth cause |
| Triage and clustering | Group violations into distinct problems | Clustering accuracy |
| Fix proposal | Propose a layout change that clears the violations | Re-running DRC on the fixed layout |


## Acknowledgements


## License

Licensed under the [Apache License 2.0](LICENSE).

## Author

Rumali Siddiqua
