# Pre-registration: three-level codes on the Set 1 dev set

Date: 2026-10-06, written and committed before the dev run. Frozen: `set1/rubric.md` v0.2
(sha256 `aca84e4687ca…`), prompt hash `00247a226a9c` (`set1/config.py`, `score.py --set 1`), model
`claude-opus-5-5`, effort `medium`. Run: `score.py --set 1 --split dev --run dev_v0.2` (all 300 dev responses).

**Purpose.** Check whether the borderline level (rubric.md §4, Levels) behaves as intended before it is used on
the remainder. This is not a test of scoring accuracy: dev scores have been studied extensively and the codebook
was built from them. Decisions about crediting borderline codes or routing responses to human review will be
pre-registered separately before the remainder run.

**Definitions.** A *code cell* is one code for one response (300 × 18 = 5,400 cells). A cell is *borderline* when
its level is 1. A response *has a borderline code* when at least one of its 18 cells is at level 1. Rater
disagreement: Score1 ≠ Score2 (32 dev responses); agreement: Score1 = Score2 (268). Responses that fail to code
(API errors after retries) are excluded and counted.

## Predictions

1. **Usage:** borderline cells are between 1% and 5% of code cells (54 to 270 of 5,400). Above 10% would suggest
   the level is used to hedge; below 0.5% would mean it adds little.
2. **Validity:** the share of responses with a borderline code among the 32 rater-disagreement responses is at
   least twice the share among the 268 agreed responses.
3. **Consistency (descriptive, no threshold):** a repeat run of the 20 pilot responses, reporting how many
   borderline cells recur at level 1.

## Reported without prediction

- Borderline cells by reason (a–f), including how often (f) "other" is used and its free-text reasons.
- Mismatches between the `borderline` entries and the level-1 codes.
- Agreement with my binary dev codes (`eda/dev_codes_v01.csv`) on present vs absent.
- Scores under the primary rule (only present counts) and with borderline also counted, against Score1.

## Results (added 2026-10-06 after the run; predictions above unchanged)

Run `dev_v0.2`: 300 of 300 coded, no errors; repeat run `dev_v0.2_repeat20`. Analysis: `eda/step6_levels_dev.py`.

1. **Usage: holds.** 90 of 5,400 cells borderline (1.67%).
2. **Validity: fails narrowly.** Responses with a borderline code: 14/32 (43.8%) of rater disagreements vs
   64/268 (23.9%) of agreements, ratio 1.83 (< 2). Exploratory, not pre-registered: restricted to credited
   codes, ratio 1.72. `eda/step6b_codes_in_disagreement.py` suggests why: in only 5 of 32 disagreements does a
   borderline code change the score; in most others the model is confident about the text and the raters
   differ on whether a clearly present item earns credit (vague materials, amount of sample, specific kind,
   mass measurement, a second surroundings item).
3. **Consistency:** on 20 repeated responses, 8 and 7 borderline cells, 6 in both; 99.2% of cells identical.

Reasons: (a) 5, (b) 5, (c) 14, (d) 46, (e) 19, (f) 1. Descriptive scores against Score1 (dev, not held out):
present only QWK 0.877, exact 0.807, SMD −0.13; borderline also counted QWK 0.896, exact 0.837, SMD −0.02.
