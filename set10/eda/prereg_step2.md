# Pre-registration: blind rule check on remainder (written before sampling)

Date: 2026-10-04. Frozen files: rubric.md sha256 0d09f0c291cb..., score_from_codes.py sha256 c1bf7d7118c9...

**Sample:** 60 responses drawn from data/set10/remainder.csv with pandas .sample(60, random_state=1).
No remainder text has been read before this point.

**Coding:** Claude codes E, J, D, N, P, L, U + flags per rubric.md section 3, blind to Score1/Score2
(dump script prints Id, color, text only). Codes saved to eda/remainder_blind_codes.csv before any join to scores.
No changes to rubric.md or score_from_codes.py after this point for this check.

**Configurations compared (score_from_codes.score):**
1. all-a   = aaaaaa (official-leaning)
2. dev-best = bababb (best of 64 on dev)
3. all-b   = bbbbbb (rater-leaning)

**Metrics:** exact match with Score1 on agreed cases (Score1 == Score2), compared with the dev figures
(0.895 / 0.929 / 0.918); QWK vs Score1 on all 60, with Score1-vs-Score2 QWK on the same 60 as reference.

## Results (appended after running eda/step3g_remainder_check.py; frozen-file hashes verified unchanged)

| config | split | agreed exact | exact vs S1 | QWK vs S1 |
|---|---|---|---|---|
| all-a | dev (fitted, n=300) | 0.895 | 0.857 | 0.846 |
| all-a | remainder (blind, n=60) | 0.865 | 0.817 | 0.831 |
| dev-best | dev | 0.929 | 0.880 | 0.871 |
| dev-best | remainder | 0.885 | 0.817 | 0.809 |
| all-b | dev | 0.918 | 0.860 | 0.859 |
| all-b | remainder | 0.885 | 0.817 | 0.809 |

Reference Score2 vs Score1 on the same 60: exact 0.867, QWK 0.875.

Observations: (1) every config drops from dev to remainder; the dev-selected config drops most
(QWK -0.062), so its dev advantage was selection overfitting. (2) On fresh data the frozen rules
are ~0.04-0.07 QWK below human-human agreement. (3) Main remainder error: rule gives 2 where
Score1 gave 1 (6 cases), mostly white/black responses with no or weak explicit effect (C2 implied
effect, O4a absolute result) -> C2/O4a may be less settled than dev suggested. Not acted on: rubric frozen.
n = 60, so QWK differences between configs (~0.02) are well within noise (CI roughly +/-0.07).
