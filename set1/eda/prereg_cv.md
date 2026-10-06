# Pre-registration: rule reliability by cross-validation, and the Set 1 test configuration

**Status: frozen 2026-10-06, committed before the remainder was coded.** Analysis code: `eda/step7_cv.py`,
checked end to end on dev codes only (no remainder or test data).

Frozen at commit: `set1/rubric.md` v0.2 (sha256 `aca84e4687ca…`), prompt hash `00247a226a9c`
(`score.py --set 1`), model `claude-opus-5-5`, effort `medium`.

## 1. Why

Dev showed three kinds of scoring rules: (1) official, from the rubric and anchors; (2) consensus, what agreeing
raters did; (3) ambiguous, where the text or the credit is uncertain. In Set 10, rules of types (1) and (2)
generalized and rules fitted to a few cases of type (3) did not. Here every rule is a **knob** applied to fixed
model codes. We pre-register a best-guess setting of every knob now, and use cross-validation on the whole
training set to rate how reliable each knob is and how prone it is to overfitting.

## 2. Data and roles

- **Train** = dev (300) + remainder (1,372) = 1,672 responses, each coded once by the model with the frozen
  prompt. Dev is already coded (`dev_v0.2`); the remainder will be coded once (`remainder_v0.2`), after this file
  is committed.
- **Change from Set 10:** the remainder is no longer a single held-out check. It becomes part of the
  cross-validated training data, and **the test set is the only hold-out**.
- **Test** = the 557 public-leaderboard responses. Not coded, not read, and no scores looked at until the single
  test run in §7.
- **Target:** Score1 (the official score). QWK is the selection metric.

## 3. Best-guess configuration (primary on test)

The score is the number of credited pieces of information, at most 3.

| Code (group) | Setting | Basis |
|---|---|---|
| VA, VT, MAT, SIZE, RT, DRY | present or borderline | official rubric; borderline also counted per dev (SMD −0.13 present-only vs −0.02) |
| Container (CS or CT) | present or borderline | official ("size/type of container") |
| Surroundings (ENVT, ENVL or ENVP) | present or borderline | consensus (agreed dev cases) |
| COVER | present or borderline | consensus (anchor 2a, dev) |
| MATV, AMT, MATK, MASS, RINSE, DESIGN | not credited | consensus (not credited on agreed dev cases), or too few cases (MATK) |
| Surroundings counting | once (any combination is one piece) | documented default (D2) |
| Container counting | once (CS and CT together are one piece) | documented default (D1) |

## 4. Knobs

- **Per-code knobs (15), each with three settings: not credited / present only / present or borderline.**
  VA, VT, MAT, SIZE, RT, DRY, container, surroundings, COVER (tiers 1–2); MATV, AMT, MATK, MASS, RINSE, DESIGN (tier 3).
- **Pooled borderline knob:** borderline counted for all credited codes vs for none. An alternative to the
  per-code borderline settings, to test whether code-specific treatment of borderline beats one rule.
- **Counting knobs (2):** surroundings once vs each of ENVT, ENVL, ENVP separately; container once vs CS and CT separately.

## 5. Cross-validation

**Folds:** 5-fold cross-validation stratified by Score1, repeated 20 times (seeds 0–19): 100 training/held-out
splits.

**Truncated transcriptions:** responses the model flags `unfinished` (a text-only flag) are excluded from the
training folds, so that settings are selected on text the raters and the model both see. They stay in the
held-out folds; out-of-fold results are reported with and without them. The flag is imperfect (some flagged
responses are complete, and cuts at a full stop are not flagged), so this removes only the detectable part of
the bias.

**Per-knob reliability.** For each knob, all other knobs stay at the best guess. In each split, the knob's
setting with the highest QWK on the training folds is *selected* (ties go to the best guess). Reported per knob:

- **Selection:** how often each setting is selected across the 100 splits.
- **Out-of-fold gain:** per repeat, QWK of the pooled held-out predictions using each split's selected setting,
  minus the same for the best guess; mean and range over the 20 repeats.
- **Optimism:** mean gain on the training folds minus mean gain on the held-out folds.

**Reliability labels (fixed now):**
- **Stable:** one setting selected in at least 80 of 100 splits.
  - *Supports the best guess* if that setting is the best guess.
  - *Contradicts the best guess* if it is another setting **and** its out-of-fold gain is positive in at least
    16 of 20 repeats.
- **Unstable:** no setting reaches 80 of 100. Treated as not supported by the data (prone to overfitting).

**Positive-control prediction:** the official codes (VA, VT, MAT, SIZE, RT, DRY, container) are selected as
credited (either credited setting) in at least 80 of 100 splits. If not, cross-validation is too noisy to act on,
and only the best guess is reported on test.

**Sensitivity analyses:** the same cross-validation on the remainder alone (nothing in the codebook was tuned
there), and excluding the six remainder responses already read (`eda/remainder_seen_ids.csv`).

## 6. Cross-validation-selected configuration (secondary on test)

**Search procedure (fixed now):** start from the best guess; go through the knobs in the order listed in §4,
changing one knob at a time to its highest-QWK setting given the others; repeat passes until nothing changes.
As in §5, responses flagged `unfinished` are left out of every set the search selects on.

- **How well the procedure itself generalizes:** nested cross-validation. Run the search on each outer training
  set (same 5 × 20 splits) and score the outer held-out fold; report out-of-fold QWK of the procedure minus the
  best guess.
- **The secondary configuration:** the search run once on all 1,672 training responses, frozen before the test run.

## 7. Test reporting (one coding run)

- Code the 557 test responses once with the frozen prompt hash; compute scores under both configurations.
- **Primary:** best guess. **Secondary:** cross-validation-selected. For each: QWK with 95% bootstrap CI, exact
  agreement, SMD, degradation against human–human QWK (train, 0.944).
- **Baselines:** bag-of-words and length-only, fit on all train (`common/baselines.py --set 1 --test`).
  Paired bootstrap differences: best guess minus bag-of-words; selected minus best guess.
- **Truncation:** everything also reported excluding responses the model flags `unfinished`.
- **Routing (descriptive):** share of test responses whose best-guess score depends on a borderline call, and
  agreement on the rest.

## 8. What stays fixed after this file is committed

The codebook, prompt, model and effort; the best-guess configuration; the knob list, settings and search order;
the fold seeds and reliability labels. The cross-validation code is written and checked on dev codes, and
committed, before the remainder results are examined.

**Cost:** remainder coding about $12.60; test about $5.10.
