# Tracker

Rule: a task is checked only when its "done" check has passed.

## Phase 0: Setup
- [x] Repo, Apache 2.0, README
- [x] pyproject.toml, venv, .gitignore
- [ ] CONTRIBUTING.md and docs/ideas.md (needed before going public)

## Phase 1: Survey
- [ ] KLayout DRC + marker DB docs
- [ ] markitdown
- [ ] TOON
- [ ] MCP overview
- [ ] ChatEDA
- [ ] Agentic EDA survey
- [x] docs/survey.md

## Phase 2: Measurement
- [x] First marker database measured
- [x] Full deck on 5 unit layouts
- [x] Verified scale sweep (384 to 38,400 markers)
- [x] Chart
- [x] Three-tokenizer comparison

## Phase 3: Benchmark pilot
- [x] 3.1 Metal1 layer number confirmed (8/0)
- [x] 3.2 Clean base layout: DRC = 0
- [x] 3.3 One injected spacing violation: DRC matches exactly
- [x] 3.4 Task JSON format + first task
- [x] 3.5 Validator script (PASS/FAIL)
- [x] 3.6 Fix check: fixed layout DRC = 0
- [x] 3.7 20 tasks at several scales, all PASS
- [x] 3.8 Clustering tasks from off-grid generator, all PASS

## Phase 4: Harness
- [ ] Task runner
- [ ] Scorer
- [ ] Cost/latency logger
- [ ] Raw baseline run (2 models)
- [ ] One transformed candidate run (2 models)

## Phase 5: Write-up
- [ ] Report
- [ ] One-command reproduction
- [ ] Sent to Mauricio
