# Pre-registration: LLM scoring of the remainder set (written before the run)

Date: 2026-10-04. Committed to git before the run starts.

## Frozen
- `rubric.md` v1.2 (sha256 `d59ff0406dc9…`), `score_from_codes.py` (sha256 `3a69da4d60e6…`).
- Scoring prompt: rubric v1.2 assembled with boundary variants `aaaaaa`, prompt hash `34e06a141c41`
  (`score.py --expect-hash 34e06a141c41`). The prompt's variant choice affects only the LLM's own score;
  configurations below are compared on scores computed from the LLM's codes.
- Model `claude-opus-5-5`, effort `medium`, one run.
- No changes to the rubric, codes or scoring rules between this run and the test run.

## Data
- All 1340 Set 10 remainder responses (`data/set10/remainder.csv`).
- 60 of them were blind-coded by Claude and their scores seen (`eda/remainder_sample_ids.csv`).
  Every metric is reported for all 1340 and for the 1280 excluding them.

## Configurations compared (score from LLM codes via `score_from_codes.score`)
| Name | B1–B6 | Rationale |
|---|---|---|
| all-a | `aaaaaa` | official-text variant of every boundary rule |
| majority | `aaaabb` | per rule, the variant the dev counts favored (B1 tie → a; B2–B4 a; B5–B6 b) |
| all-b | `bbbbbb` | non-official variant of every rule |

## Metrics
- Primary: QWK vs Score1, percentile bootstrap 95% CI (2000 resamples).
- Secondary: exact agreement, SMD, degradation vs Score1–Score2 QWK on the same responses;
  paired bootstrap CI for each config's QWK minus all-a's.

## Selection rule
- The configuration with the highest remainder QWK (all 1340) is selected for the test set.
- The test set is scored **once** with the same prompt (hash `34e06a141c41`). Test results are reported for
  the selected configuration **and** for all-a, so the selection effect is visible.

## Baselines (fixed before seeing test results)
- Length-only and bag-of-words logistic regression, fit on all 1640 Set 10 train responses, evaluated on test.
