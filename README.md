# LLM Short-Answer Scoring with a Written Codebook (ASAP-SAS, Set 10)

Can a large language model score student short answers the way trained human raters do? This project scores one grade 8 science item from the ASAP Short Answer Scoring dataset with Claude Opus 5.5. The model works from a written codebook developed on a 300-response labeled development set, and it uses no labels at scoring time. Its scores are evaluated against the official human scores with quadratic weighted kappa (QWK), the field-standard agreement metric for this task.

## Results (competition public test set, one pre-registered run, n = 546)

| Scorer | QWK [95% CI] | Exact agreement | SMD |
|---|---|---|---|
| **LLM + codebook (pre-registered configuration)** | **0.763** [0.719, 0.805] | 0.80 | +0.07 |
| LLM + codebook (official-leaning configuration) | 0.775 [0.729, 0.817] | 0.79 | −0.08 |
| Bag-of-words logistic regression (trained on 1,640 labeled responses) | 0.709 [0.653, 0.754] | 0.78 | +0.09 |
| Length-only logistic regression | 0.457 [0.394, 0.516] | 0.62 | +0.07 |
| *Second human rater vs. first (train set, for orientation)* | *0.884* | *0.89* | *−0.03* |

*QWK* measures agreement on an ordinal scale, corrected for chance, with disagreements penalized by their squared size: 1 is perfect agreement, 0 is chance. *SMD* (standardized mean difference) is the mean machine score minus the mean human score, divided by their pooled standard deviation; positive means the machine is more lenient. Confidence intervals are percentile bootstraps over responses.

- **Against the supervised baseline**, the LLM is modestly better. The paired bootstrap difference on the same 546 responses is +0.054 [+0.002, +0.109] for the pre-registered configuration and +0.065 [+0.011, +0.123] for the official-leaning one. This paired test was added after the test run and was not pre-registered.
- **Against operational guidelines** for automated scoring (Williamson, Xi & Breyer, 2012): machine–human QWK of at least 0.70, chosen there as the "tipping point" at which signal outweighs noise; machine–human QWK and Pearson correlation each no more than 0.10 below human–human agreement; and |SMD| ≤ 0.15. The pre-registered configuration meets the 0.70 floor (QWK 0.763, r 0.767) and the SMD limit, and narrowly misses the degradation guideline (QWK 0.12 and r 0.12 below human–human; the official-leaning configuration is 0.109 and 0.103 below). The authors treat these as guidelines rather than hard cutoffs and report using a model operationally whose machine–human QWK was 0.69 against a human–human 0.71. The human–human figures are from the training set, because the test set has a single human score per response, so the degradation comparison is approximate.
- **Full-scale disagreements are rare.** The LLM gave 0 where the human gave 2, or the reverse, on 2 of 546 test responses (0.4%); the bag-of-words baseline did so on 3, and the two human raters never did across the 1,640 training responses. High-stakes programs often treat scores one point apart as agreement, but on a 0–2 scale one point is half the range, so that convention is not applied here.
- **The two configurations are interchangeable.** The pre-registered selection rule picked the rater-leaning configuration because it was +0.010 better on the validation set; on test it was −0.011 [−0.044, +0.020] worse. The selection was effectively a coin flip.
- **Most disagreement is at the boundary between 0 and 1**, where the two configurations err in opposite directions: the official-leaning one is harsher and the rater-leaning one more lenient.

## The item and the data

[ASAP-SAS](https://www.kaggle.com/c/asap-sas) is a 2012 Kaggle competition sponsored by the Hewlett Foundation: ten short-answer items, each with about 1,700 student responses scored by two trained raters. Set 10 ("Doghouse") is a grade 8 science item. Students read about an experiment measuring the air temperature in glass jars with black, dark gray, light gray and white lids under a lamp (averages 53, 48, 45 and 42 °C), then chose a paint color for a doghouse, described how that color would affect the inside of the doghouse, and supported the choice with the experiment's results. Responses are scored 0–2. Set 10 is the starting point among the five science items: its scoring guide lists explicit components, its score distribution is balanced (18% / 47% / 35%) and its raters agree well (exact agreement 0.885, QWK 0.884). Sets 1 and 2 are similar and are left for extension; the two biology items (Sets 5 and 6) were ruled out because 77–84% of their responses score 0, too few high scores to evaluate.

**Splits.** The 1,640 Set 10 training responses were split into a **development set** of 300 (random, seed 0), used to write and revise the codebook, and a **remainder** of 1,340, used once as a validation set to choose between pre-registered configurations. The **test set** is the competition's public test set: Kaggle competitions score entries on a "public leaderboard" during the competition and a "private leaderboard" at the end, and the answer key was later released for the public portion only. Test texts come from `public_leaderboard_rel_2.tsv` (identical to the first release for Set 10) and labels from `public_leaderboard_solution.csv`. The private portion has no released labels and is unused.

**Transcription.** Responses were handwritten and transcribed with spelling and grammar errors preserved. Digitization also inserted a space at each handwritten line wrap, splitting words ("dogho use"); this was found from the regular spacing of the artifact (first at character 45, then about every 73 characters). Each response begins with the color the student selected from a menu.

## The codebook

The codebook ([rubric.md](rubric.md)) separates *what a response contains* from *how that becomes a score*. A rater, human or LLM, first records codes, then applies ranked scoring rules.

**Codes:** E, the effect of the chosen color on the doghouse interior; J, a two-sided "not too hot, not too cold" claim; D, a temperature comparison between colors; N, an experiment result cited; P, a result that places the chosen color relative to another lid; L, a jar temperature read as the doghouse's own temperature; U, a misunderstanding of the experiment or the science (off-target reasoning, warmth "at night", contradiction). Flags mark special cases such as a restated hypothesis or a menu color that differs from the argued color.

**Rules** are tiered by source. **O** rules come from the official rubric, the item's scoring guide and the anchor papers. **C** (consensus) rules describe what the two raters did when they agreed, found by coding all 300 development responses (first blind to the scores, then sharpened after seeing them). **B** (boundary) rules cover cases where raters disagreed and come in an official-leaning variant (*a*) and a rater-leaning variant (*b*). **S** is a candidate tendency of one rater. Two findings from building the codebook:

- **Raters credited an implied effect.** For white or black, "white was the coolest lid, 42 °C" earned full credit by rater consensus without an explicit statement about the doghouse, which the literal rubric requires.
- **Gray choices needed comparative evidence.** A result about the gray lid alone ("light gray averaged 45 °C") rarely earned full credit. The item's own scoring guide explains this: its examples of acceptable evidence are absolute for white and black but comparative for the grays ("8 °C cooler than black").

## Scoring pipeline

[`score.py`](score.py) sends each response to `claude-opus-5-5` (effort `medium`) with the codebook as a cached system prompt and requests structured output against a JSON schema: the seven codes, flags, a one-sentence rationale and a score. [`score_from_codes.py`](score_from_codes.py) maps codes to scores deterministically; the model's own score matched the code-derived score on 99.9% of remainder responses. Because scoring rules are applied to the codes, every rule variant can be evaluated from one model run. Each run is pinned to a hash of the assembled prompt, and the script refuses to resume or start if the prompt has changed. Scoring cost about $0.0065 and 4 seconds per response; the whole project used about $16 of API calls. Two repeat runs on the development set gave identical scores for 98.3% of responses, a run-to-run QWK difference of 0.006.

**Baselines** ([`baselines.py`](baselines.py)) are fit on all 1,640 training responses with nested 5-fold cross-validation: a length-only logistic regression on log word count, and unigram-plus-bigram counts with regularized logistic regression. Repairing the line-wrap artifact before counting words ([`text_clean.py`](text_clean.py)) changed bag-of-words QWK by only +0.002.

## Evaluation design and pre-registration

- The codebook was developed on the 300 development responses only. Evaluation used the 1,340-response remainder once and the test set once.
- Before the remainder run, the prompt, the three candidate configurations, the selection rule and the reporting plan were written to [`eda/prereg_remainder.md`](eda/prereg_remainder.md) and committed to git (commit `5ab8e87`, 2026-10-04 19:47). The remainder results were committed at 21:25 and the single test run completed at 22:13. Git timestamps are local and self-reported, so this is a paper trail, not proof.
- An earlier blind check of the rules on 60 remainder responses was planned in [`eda/prereg_step2.md`](eda/prereg_step2.md) before sampling, but that file was first committed later, so its trail is weaker. Those 60 responses are reported with and without exclusion; excluding them changes remainder QWK by at most 0.004.
- Development-set estimates were optimistic, as expected for rules tuned there: 0.820–0.835 on development, 0.740–0.750 on the remainder, 0.763–0.775 on test.

## Prompt iterations

| Version | Change | Why |
|---|---|---|
| v1.0 | Code-based codebook | Prose rubric replaced by codes plus ranked rules, so detection and scoring can be evaluated separately |
| v1.1 | Narrowed "self-contradiction" | In a 20-response pilot, the model read seasonal answers ("cooler in summer, warmer in winter") as contradictions, because the codebook's own example had that form |
| v1.2 | Moved the misconception rule below full credit | In the development runs, four answers that both raters scored 2 were zeroed because they also contained a misconception (e.g., "keeps the dog warm at night"). Reordering raised development QWK from 0.776 to 0.820; on fresh data, reversing it costs 0.029–0.038 |

## Error analysis

Eight test disagreements under the pre-registered configuration, chosen to cover different causes: the two severe errors first, then the rest in the order the scoring rules are applied. Responses are paraphrased; IDs refer to the ASAP-SAS public test set, so readers with the data can check the originals.

**Severe errors**

1. **Response 27908, human 0, LLM 2: the implied-effect rule over-credits a bare citation.** The student chose black only because it had the highest average temperature (53 °C) and said nothing about what that would do to the doghouse. The consensus rule that lets a cited comparison stand in for the effect (C2) gave full credit under the white/black full-credit rule (O4a). The official rubric's 1-point description includes a response that cites experiment results but omits the effect on the doghouse, which fits this response; the human gave 0, perhaps reading it as showing no understanding of why the highest temperature matters (none of the official anchor papers covers this case).
2. **Response 27982, human 2, LLM 0: a coding miss compounded by a rule.** The student said white turns sunlight away, so the doghouse stays around 40–45 °C. The model did not code the implied cooling effect, and the rule for reading jar temperatures as doghouse temperatures (B2) then removed all credit.

**Full credit**

3. **Response 27641, human 1, LLM 2: a literal reading the rater did penalize.** The student contrasted black's 53 °C with white's 42 °C as if those were the doghouse's summer temperatures. The codebook's rule that a literal reading costs nothing once full credit is met (C5, based on six agreeing development cases, all gray) gave 2; the rater evidently treated the misreading as undermining the argument.
4. **Response 28120, human 2, LLM 1: the gray placement rule, plus a scoring rule leaking into coding.** The student argued for light gray as a compromise between white (too cold) and black (too hot), citing the experiment's finding that darker lids got hotter. The model treated that citation as the task's hypothesis restated (flag `hyp`, boundary rule B3), a rule that was in its prompt and so applied while coding, so light gray was never placed by evidence (P = 0) and gray full credit (O4b) failed.

**Misconception versus full credit (the v1.2 ordering)**

5. **Response 27869, human 2, LLM 2: the ordering working.** The student said black would insulate the doghouse, a misconception, but also stated that it would keep the inside warm and cited black's highest average. Because full credit (O4a) outranks the misconception rule (C1), the response kept its 2, matching the human.
6. **Response 28066, human 1, LLM 2: the same ordering failing.** The student said black is best at taking in and holding heat and cited its 53 °C average, without saying what that does to the doghouse. Full credit came only through the implied-effect rule (C2); the human gave 1. Of the 8 test responses where the ordering let a misconception keep full credit, the human agreed on 5; in 2 of the 3 disagreements the effect was only implied. That suggests raters tolerate a misconception when the effect is stated but not when it is implied, an observation from too few cases to turn into a rule by hand.
7. **Response 27599, human 1, LLM 0: the misconception rule is too strong below full credit.** The student argued black would let less air into the doghouse (off-target) but also cited black's 54 °C jar reading. The misconception rule (C1) gives 0 for any misconception short of full credit; the human gave partial credit for the correct use of data.

**Boundary rules**

8. **Response 27657, human 0, LLM 1: the weakest boundary rule.** The student chose white because it takes in the least energy, with no effect on the doghouse and no experiment result. The rater-leaning variant of the physics-claims rule (B6.b) gave 1; the human gave 0. This rule was wrong on 51% of the remainder responses it decided.

| # | Response | Human | LLM | Codes present (LLM) | Deciding rule |
|---|---|---|---|---|---|
| 1 | 27908 | 0 | 2 | D, N, P | Full credit, white/black (O4a), via implied effect (C2) |
| 2 | 27982 | 2 | 0 | N, L | Literal reading without placement (B2) |
| 3 | 27641 | 1 | 2 | E, D, N, P, L | Full credit (O4a); literal reading ignored (C5) |
| 4 | 28120 | 2 | 1 | J, D; flag `hyp` | Partial credit (O2, C3); gray full credit (O4b) failed: no P |
| 5 | 27869 | 2 | 2 | E, D, N, P, U | Full credit (O4a) outranks misconception (C1) |
| 6 | 28066 | 1 | 2 | D, N, P, U | Full credit (O4a) via C2, outranks C1 |
| 7 | 27599 | 1 | 0 | N, U | Misconception (C1) |
| 8 | 27657 | 0 | 1 | flag `physics` | Physics-only claim (B6, variant b) |

Codes are those defined in [the codebook](#the-codebook): E effect, J just right, D direction, N result, P placed, L literal, U misunderstanding; rule IDs refer to [rubric.md](rubric.md). In five of the eight cases the deciding rule runs through the implied-effect rule (C2) or the misconception rule (C1).

Across the 108 test disagreements, the misconception rule (C1) decided 16 of the 18 the LLM scored 0 against a human 1, the full-credit rules (O4a, O4b) all 27 it scored a point too high, and the physics-claims rule (B6) 21 of the 39 it scored 1 against a human 0.

## What the rules contributed (exploratory)

This analysis was done after the test run and does not change the reported result. Numbers are for the remainder set (n = 1,340), with the test set (n = 546) as replication.

**Tiers.** The official rubric alone, applied literally, reaches QWK 0.699 (test 0.692), below the 0.70 operational floor. Adding the consensus rules raises this to 0.769 (test 0.791). Most of that gain comes from a single rule: counting "not too hot, not too cold" as a description of the effect for a gray paint choice. Adding the boundary rules *lowered* QWK (0.750; test 0.763), mostly through one rule that gave partial credit to general physics claims, which was wrong half the time it fired. The rater-specific rule lowered it sharply (0.630).

**Ordering.** The scoring rules form a ranked list in which the first applicable rule decides. Across all 5,040 orderings of the seven ranked rules, QWK ranged from 0.23 to 0.77, but only 72–169 distinct score patterns arose: most orderings are equivalent. Nearly all the variation came from one requirement: the full-credit rule must outrank the general partial-credit rules, the "specific before general" principle known in linguistics as the Elsewhere Condition. The one substantive ordering choice was whether a misconception should override an otherwise complete answer (the v1.2 change, above). The best of all 5,040 orderings beat the one used by only about 0.01, within selection noise.

**A hypothesis about rule selection.** Rules supported by many agreeing human decisions generalized to new data; rules written to resolve a handful of edge cases (3–7 examples each) did not, and as a group they made the scorer worse. In retrospect this is the familiar bias–variance trade-off applied to a codebook: each boundary rule was a parameter fit to a few development cases. A simpler codebook, official plus consensus rules only, scored best on both held-out sets. That was observed after seeing those sets, so it is a hypothesis for the next iteration rather than a result.

## Limitations

- **Possible contamination.** ASAP-SAS has been public since 2012, including the answer key for the test set used here. The model may have seen the items, responses or scores during training, and this cannot be ruled out. Scoring from auditable codes, rather than asking for a score directly, makes a memorized score less directly usable but does not remove the concern.
- **One item, one model.** Results are for a single, well-specified science item with a component-based rubric, and for one model at one effort level. Items with holistic rubrics, and lower human agreement, are likely harder.
- **Approximate human reference.** The test set has one human score per response, so human–human agreement comes from the training set.
- **No subgroup analysis.** The data has no demographic information, so the fairness checks used in operational scoring (score differences by subgroup) could not be run.
- **Codebook built by one coder.** The development codes that the rules were derived from were assigned by Claude, with spot checks by the author, not by independent trained raters.
- **A design flaw in the prompt.** Two boundary rules changed a code rather than a score (for example, "a restated hypothesis does not count as a result"). Because the chosen variant was in the prompt, the model applied it while coding, so the other variant could not be tested afterwards.

## Future work

- **Cross-validate the rules themselves.** Because rules are applied to fixed model codes, rule sets and orderings can be selected inside k-fold cross-validation on the training data: choose on k−1 folds, score the held-out fold, repeat. This estimates honestly how much rule selection helps, and rules chosen consistently across folds identify the key rules (a form of stability selection), replacing judgment from a few dozen development cases.
- **Ask the model only for observations.** Keep every scoring decision, including code-changing rules, out of the prompt and apply it afterwards.
- **Route unusual responses to human raters.** Operational systems flag responses with abnormal characteristics (very long or very short, repetitive, off-topic) for human scoring rather than scoring them automatically. The codebook's misunderstanding code and flags are natural routing signals; the trade-off between the share of responses sent to humans and the resulting agreement could be measured from the existing codes.
- **Extend to other items** (ASAP-SAS Sets 1 and 2 are the other balanced science items) to see whether codebook-based scoring holds up when human agreement is lower.

## References

Hewlett Foundation (2012). *The Hewlett Foundation: Short Answer Scoring* [Data set and competition]. Kaggle. https://www.kaggle.com/c/asap-sas

Williamson, D. M., Xi, X., & Breyer, F. J. (2012). A framework for evaluation and use of automated scoring. *Educational Measurement: Issues and Practice, 31*(1), 2–13. https://doi.org/10.1111/j.1745-3992.2011.00223.x

## Data

This project uses the ASAP Short Answer Scoring dataset (Set 10 only). It is available from the [Kaggle competition page](https://www.kaggle.com/c/asap-sas) after accepting the competition rules; see the page's Rules tab for the terms of use. The data is not redistributed here.

**Files needed in `data/`:** `train.tsv` (training responses with both human scores), `public_leaderboard_rel_2.tsv` (public test responses) and `public_leaderboard_solution.csv` (public test scores). The scoring guide and anchor papers (`Data_Set_Descriptions.zip`, `Training_Materials.zip`) were used to write the codebook but are not needed to rerun it.

**Not included, because they quote student responses:** model outputs with rationales (`results/*.jsonl`), the hand-coding files (`eda/*_codes.csv`) and generated reading lists. Analyses that read these files can be rerun after scoring the data yourself.

**Included:** code, the codebook, pre-registrations, prompt snapshots (`results/*.prompt.txt`), and baseline predictions keyed by response ID (`results/baselines_test_predictions.csv`). Response IDs refer to the ASAP-SAS files and contain no student information.

## Reproducing

Requires [pixi](https://pixi.sh) and an Anthropic API key in `ANTHROPIC_API_KEY`. Scoring the test set costs about $3.50.

```bash
pixi run python make_split.py 10
pixi run python baselines.py --test
pixi run python score.py --split test --run test_v1.2 --cfg aaaaaa --expect-hash 34e06a141c41
pixi run python eda/test_analysis.py
```

Model outputs will differ slightly from run to run (repeat runs on the development set agreed on 98.3% of scores).

## License and citation

Code is released under the [MIT License](LICENSE). The written documents (this README, the codebook and the notes in `eda/`) are released under [CC BY 4.0](LICENSE-docs.md). The ASAP-SAS item text, data table and scoring-guide material reproduced in the codebook and prompt snapshots belong to their owners and are not covered by either license; see [LICENSE-docs.md](LICENSE-docs.md). To cite this work, use [CITATION.cff](CITATION.cff) (GitHub shows a "Cite this repository" button).
