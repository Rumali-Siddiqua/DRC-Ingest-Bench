# Frozen experiment environment

All Phase 2 and Phase 3 results were produced with exactly this setup.

| Item | Value |
|------|-------|
| IHP-Open-PDK commit | 5e6d592e4002946a4616f798c357f0f3c06cf3b6 |
| KLayout binary (runs the deck) | 0.30.7 |
| klayout Python package (reads reports) | 0.30.12 |
| PDK-pinned KLayout version (versions.txt) | 0.30.5 |
| Deck options | --no_density --run_mode=flat |
| Rule values | deck default (no --drc_json passed) |
| Tokenizers | tiktoken cl100k_base, tiktoken o200k_base, Qwen/Qwen2.5-7B-Instruct |

Note: the binary (0.30.7) is newer than the PDK's pinned version (0.30.5). This is
recorded deliberately rather than corrected, since all results were produced with it.
KLayout DRC results are known to be version-sensitive, so this must be stated with
any published number.
