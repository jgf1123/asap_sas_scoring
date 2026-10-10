# LLM Short-Answer Scoring with a Written Codebook (ASAP-SAS, Set 1)

*Part of [asap_sas_scoring](../README.md). Builds on the [Set 10 study](../set10/README.md) and applies its lessons.*

Can a large language model score student short answers the way trained human raters do, if it only records
what each response contains and leaves the scoring to explicit rules? This study scores one grade 10 science
item from the ASAP Short Answer Scoring dataset with Claude Opus 5.5. The model records codes from a written
codebook developed on a 300-response labeled development set; deterministic rules turn the codes into a score.
On the competition's public test set it reaches **QWK 0.895**, well above a bag-of-words model trained on 1,672
labeled responses (0.720) and 0.049 below agreement between two human raters.

## Results (competition public test set, one pre-registered run, n = 557)

| Scorer | QWK [95% CI] | Exact agreement | SMD |
|---|---|---|---|
| **LLM codes + rules (pre-registered primary)** | **0.895** [0.862, 0.922] | 0.84 | +0.02 |
| LLM codes + rules (cross-validation-selected, secondary) | 0.898 [0.870, 0.922] | 0.83 | −0.05 |
| Bag-of-words logistic regression (trained on 1,672 labeled responses) | 0.720 [0.671, 0.762] | 0.56 | −0.07 |
| Length-only logistic regression | 0.257 [0.180, 0.336] | 0.36 | +0.02 |
| *Second human rater vs. first (train set, for orientation)* | *0.944* | *0.89* | *−0.01* |

*QWK* (quadratic weighted kappa) measures agreement on an ordinal scale, corrected for chance, with
disagreements penalized by their squared size: 1 is perfect agreement, 0 is chance. *SMD* is the mean machine
score minus the mean human score, divided by their pooled standard deviation; positive means more lenient.
Confidence intervals are percentile bootstraps over responses.

- **Against the supervised baseline:** +0.175 QWK [+0.130, +0.222] on the same 557 responses (paired bootstrap,
  pre-registered).
- **Against operational guidelines** (Williamson, Xi & Breyer, 2012): QWK at least 0.70; machine–human QWK and
  Pearson correlation no more than 0.10 below human–human; |SMD| ≤ 0.15. The primary scorer meets all three:
  QWK 0.895, degradation 0.049 (Pearson 0.048), SMD +0.02. The human–human figures come from the training set,
  because the test set has one human score per response.
- **The two pre-registered configurations are interchangeable:** the secondary is +0.003 [−0.010, +0.018].
- **Truncated transcriptions:** without the 13 responses (2.3%) the model flagged as cut off, QWK is 0.913.
- **Routing:** 11.7% of responses have a score that depends on a borderline call. On the other 88.3%, exact
  agreement is 0.884 (QWK 0.925), close to the two human raters' 0.894. These are the natural candidates for
  human review.
- **Full-scale disagreements** (0 vs 3) occurred on 2 of 557 responses; the two human raters never disagreed by
  three points across 1,672 training responses.

## The item and the data

Set 1 ("Acid Rain") is a grade 10 science item. Students read a group's procedure for soaking four materials
(marble, limestone, wood, plastic) in vinegar for 24 hours and weighing them before and after, with a table of
results. They then describe what additional information they would need to replicate the experiment,
naming at least three pieces. The item rubric is a count: three pieces of needed information earn 3 points,
two earn 2, one earns 1. It lists seven accepted pieces (amount and type of vinegar, which materials, sample
size, rinse time, drying method, container size or type) and ends with "other acceptable responses".

**Data.** 1,672 training responses, each scored by two raters (exact agreement 0.894, QWK 0.944); scores are
balanced (23% / 26% / 31% / 20% for 0–3). The test set is the 557 public-leaderboard responses with released
labels (one score per response). Train was split into a **development set** of 300 (random, seed 0), used to
build the codebook, and a **remainder** of 1,372.

**Transcription.** Responses were handwritten and transcribed. Paragraph breaks appear as `^p`; they are sent to
the model as line breaks, because students used them to separate items. Some transcriptions are **cut off**:
both raters scored the full handwritten answer, but the text ends mid-sentence. Of 300 development responses
the model flagged 10 as unfinished; about half of those were scored by both raters above what their visible
text supports.

## What changed from Set 10

Set 10 ended with four lessons; this study applies each.

| Set 10 lesson | Applied in Set 1 |
|---|---|
| Walk through the data before design choices | data format, human agreement, truncation and anchor papers examined before any coding |
| Consensus rules before boundary rules | rules come from the rubric, the anchors, and what agreeing raters did; there is no boundary tier |
| Keep every scoring decision out of the prompt | the model records codes only; it never sees a score or a scoring rule |
| Select rules by cross-validation, not from a few cases | every rule is a knob rated by repeated cross-validation on all training data |

Two further changes came from the data: codes are recorded at **three levels** (present, borderline, absent),
and the remainder became cross-validation data, leaving **the test set as the only hold-out**.

## The codebook

The codebook ([rubric.md](rubric.md)) gives the task as students saw it, reading notes, a coding principle, and
18 codes. The coding principle: record a code only when the response presents that information as **missing or
needed**, not when it lists equipment, suggests a change, restates the procedure, or uses a catch-all phrase.

| Source | Codes | Credited? |
|---|---|---|
| **Rubric list** | VA amount of vinegar, VT type of vinegar, MAT which samples, SIZE sample size or shape, RT rinse time, DRY drying method, container size or type | yes |
| **Anchor papers** | COVER whether to cover the containers | yes |
| | MASS how to measure mass (anchor 1a: not credited) | no |
| **Discovered from responses** | surroundings: temperature, light, location during the 24 hours | yes |
| | MATV vague "materials", AMT amount of sample, MATK specific kind of sample, RINSE rinse-water details, DESIGN control or trials | no |

Several discovered codes are refinements of rubric items found by comparing codes with scores: "how much of
each sample" (AMT) behaved differently from size or shape (SIZE), and vague "materials" (MATV) differently from
asking which samples (MAT). Recording uncredited codes keeps the model's job descriptive; whether a code earns
credit is a rule outside the prompt.

**Levels.** Each code is recorded as present, borderline or absent. Borderline requires a stated reason: vague
wording, an unclear or possibly mistaken referent, garbled or cut-off text, framing (equipment, suggestion,
restatement), two readings, or another reason given in words. On 300 development responses the model used the
borderline level for 1.7% of code cells, and repeated runs gave the same level for 99.2% of cells.

## Scoring pipeline

[`score.py`](../score.py) sends each response to `claude-opus-5-5` (effort `medium`) with codebook sections 1–4
as a cached system prompt and requests structured output: 18 codes at three levels, borderline reasons, flags
(including `unfinished`), other information named, and a rationale. Rules in
[`score_from_codes.py`](score_from_codes.py) and [`eda/step7_cv.py`](eda/step7_cv.py) compute the score: the
number of credited pieces, at most 3. Each run is pinned to a hash of the assembled prompt. Coding cost about
$0.010 and 5 seconds per response; the whole study used about $23 of API calls.

**Baselines** ([`baselines.py`](../common/baselines.py)): unigram-plus-bigram counts with regularized logistic
regression, and a length-only logistic regression, both trained on all 1,672 training responses.

## Evaluation design and pre-registration

- **Three-level codes** were pre-registered on the development set before use
  ([`eda/prereg_levels.md`](eda/prereg_levels.md), commit `ebdbbc2`). The usage prediction held (borderline in
  1–5% of code cells: 1.7%). The validity prediction failed narrowly: responses with a borderline code were 1.8
  times as common among rater disagreements as among agreements, against a predicted 2 times. Most rater
  disagreements turned out to be about whether a clearly present item earns credit, not whether it is present.
- **The test configurations** were pre-registered before the remainder was coded
  ([`eda/prereg_cv.md`](eda/prereg_cv.md), commit `93ffad7`): a **best guess** from the rubric, anchors and
  development-set consensus (primary), and a configuration chosen by a fixed search under cross-validation
  (secondary). The cross-validation results (commit `7535165`) and the test report script (commit `23731f1`)
  were committed before the single test run. Git timestamps are local and self-reported, so this is a paper
  trail, not proof.
- **Truncation:** responses the model flagged `unfinished` were left out of all rule selection, and results
  are reported with and without them.

## What cross-validation said about the rules

Every rule was treated as a knob applied to fixed model codes and rated by 5-fold cross-validation repeated 20
times on all 1,672 training responses ([`eda/step7_cv.py`](eda/step7_cv.py)). For each knob: how often each
setting was selected on training folds, the gain on held-out folds, and optimism (training gain minus held-out
gain).

- **Positive control passed:** every rubric code was selected as credited in 100 of 100 splits.
- **Uncredited codes stayed uncredited** in 100 of 100 splits each, although crediting them would rescore up to
  271 responses: the development-set consensus generalized.
- **Counting defaults held:** surroundings and container details count once (100 of 100).
- **Borderline credit is code-specific.** Borderline calls on MAT and VT should not count (selected in 100 of 100,
  out-of-fold gains +0.006 and +0.003); on SIZE, RT, DRY, container and COVER they should; VA and surroundings were
  unstable. A single rule for all borderline calls lost to per-code treatment. On agreed training responses,
  raters accepted borderline calls from 18% (VT) and 28–30% (VA, MAT) to 68–78% (SIZE, RT) of the time; when a
  credited code was clearly present, they accepted it 85–97% of the time regardless of where the code came from.
- **The search itself** beat the best guess by +0.004 QWK out of fold (20 of 20 repeats); on test the
  difference was +0.003 and not significant.

## What reading responses and borderline credit contributed (exploratory)

A 2 × 2 ablation on the remainder (n = 1,372; nothing in the codebook was fitted there) separates the credited
codes from the threshold ([`eda/step10_ablation.py`](eda/step10_ablation.py)).

| | Present only | Present or borderline |
|---|---|---|
| **Rubric codes only** | QWK 0.821, SMD −0.23 | QWK 0.834, SMD −0.12 |
| **Rubric + discovered codes** | QWK 0.877, SMD −0.11 | QWK 0.881, SMD +0.01 |

- **Discovered codes** add about 0.05 QWK [0.04, 0.07]. With rubric codes alone the scorer misses the
  degradation guideline (0.821 against the 0.844 needed) and is clearly harsh (SMD −0.23).
- **Borderline credit** barely changes QWK (+0.005 to +0.012, intervals including 0) but removes the bias:
  counting only clear mentions under-scores systematically.

## Error analysis

The 90 test disagreements with the primary scorer split by direction ([`eda/step13_test_errors.py`](eda/step13_test_errors.py)).
Each is assigned to the first cause that applies:

| Cause | Model too high | Model too low |
|---|---|---|
| Truncated transcription | – | 7 |
| Borderline credit raised the score | 28 | – |
| An uncredited item the human credited (vague materials, amount of sample, mass measurement, rinse water) | – | 26 |
| Clearly present codes, lower human score | 23 | – |
| Other | – | 6 |

Seven disagreements were two or more points apart: four truncated transcriptions, two cases of borderline
stacking, and one with clearly present codes. Responses are paraphrased; IDs refer to the ASAP-SAS public test set.

1. **Response 1850, human 3, model 0: truncation.** The transcription is a five-word opening clause that names
   nothing; the rater scored the full answer. No text-based scorer can recover this.
2. **Response 1930, human 0, model 3: borderline stacking.** The student listed shape, size and "liquid" without
   saying of what. The single word "liquid" became a borderline amount of vinegar *and* a borderline type of
   vinegar, so one vague word earned two points.
3. **Response 2025, human 0, model 2: stacking from catch-alls.** A complaint that the procedure lacks "the
   amount of everything" and what to use produced several borderline codes from two vague phrases.
4. **Response 2018, human 0, model 2: clearly present codes.** The student asked for the amount of vinegar and
   which materials go in each cup. The codes are unambiguous; the human score cannot be checked without a second
   rater.
5. **Response 1687, human 1, model 0: an uncredited item credited.** The student asked for a list of materials and
   how to determine the mass, two items development raters did not credit when they agreed.
6. **Response 2091, human 3, model 2: surroundings counted separately.** The student asked for the temperature,
   whether the room should be light or dark, and the amount of vinegar. The rater counted temperature and light as
   two pieces; the rules count surroundings once, which matched the training raters in 19 of 25 such cases.

**What the human raters did differently (training data, exploratory).** When the two training raters disagreed,
the model's score matched the second rater's in 88 of 145 remainder disagreements and the first rater's in 53; its
agreement over all remainder responses was QWK 0.894 with the second rater and 0.881 with the first, the official
score. Most disagreements involved one rater crediting an item the codes mark as uncredited, or withholding a point
for items the codes mark as present. Items that earn nothing alone did raise human scores gradually: with two such
items, raters gave an extra point 14–26% of the time, so "two partial items make one point" is not the rule.

## Limitations

- **Possible contamination.** ASAP-SAS and its public answer key have been online since 2012; the model may have
  seen them in training. Scoring from codes makes a memorized score less directly usable but does not remove the
  concern.
- **One coder built the codebook.** The development codes were assigned by Claude, the same model family that
  scores, with checks by the author. Agreement between the model and those codes (1 of 360 code cells different
  in a pilot) shows consistency, not validity.
- **A counting item.** The rubric counts pieces of information, which maps naturally onto codes. Items judged on
  quality are likely harder.
- **One human score on test.** Model error and rater idiosyncrasy cannot be separated on the test set, and
  human–human agreement comes from the training set.
- **Truncated transcriptions** put a floor under every text-based scorer; some truncation ends at a full stop and
  cannot be detected.
- **No subgroup analysis:** the data has no demographic information.

## Future work

- **Evidence spans.** Ask the model for the exact words behind each code. Spans would make two error sources
  checkable: short or generic evidence (one word such as "liquid") may predict rejected borderline calls better
  than the borderline label, and one span supporting several codes could count once. Both would be rules outside
  the prompt, rated by the same cross-validation, and evaluated on a new hold-out because this test set is spent.
- **Simpler stacking rules first.** "At most one borderline credit per response" or borderline credit by reason
  can be tested on the existing training codes without new model runs.
- **Independent human coding** of a sample of responses with the codebook, to check that the codes capture what
  people see, not only what Claude sees.
- **Routing as an operational result:** a curve of the share of responses sent to human raters against agreement
  on the rest, using borderline dependence, the `unfinished` flag and, later, span signals.
- **A sharper vague-materials code.** A request for a list of materials earns credit about a third of the time,
  mostly at the 0/1 line; a finer distinction might separate the credited cases.
- **Other items.** Set 2 also lists experimental-design improvements with "other acceptable responses", but its
  rubric judges the quality of an answer rather than counting pieces. Codes there would have to describe quality,
  so the codebook would not transfer; whether the process (tiers, levels, cross-validated rules) does is an open
  question.

## Data

This study uses the ASAP Short Answer Scoring dataset (Set 1 only), available from the
[Kaggle competition page](https://www.kaggle.com/c/asap-sas) after accepting the competition rules. The data is
not redistributed here.

**Files needed in `data/`:** `train.tsv`, `public_leaderboard_rel_2.tsv` and `public_leaderboard_solution.csv`.
The scoring guide and anchor papers (`Data_Set_Descriptions.zip`, `Training_Materials.zip`) informed the codebook
but are not needed to rerun it.

**Not included, because they quote student responses:** model outputs (`results/*.jsonl`) and the development
coding files (`eda/*_codes*.csv`). **Included:** code, the codebook, pre-registrations, prompt snapshots
(`results/*.prompt.txt`), cross-validation and test reports, override files and baseline predictions keyed by
response ID.

## Reproducing

Requires [pixi](https://pixi.sh) and an Anthropic API key in `ANTHROPIC_API_KEY`. Run from the repository root.
Coding the test set costs about $6; coding all training responses for the cross-validation about $17.

```bash
pixi run python common/make_split.py 1
pixi run python common/baselines.py --set 1 --test
pixi run python score.py --set 1 --split test --run test_v0.2 --expect-hash 00247a226a9c
pixi run python set1/eda/step12_test_report.py
```

The cross-validation additionally needs `score.py --set 1 --split dev --run dev_v0.2` and `--split remainder
--run remainder_v0.2`, then `set1/eda/step7_cv.py set1/results/dev_v0.2.jsonl set1/results/remainder_v0.2.jsonl`.
Model outputs differ slightly from run to run (99.2% of code cells repeated exactly on 20 development responses).

## License and citation

Code is released under the [MIT License](../LICENSE). The written documents (this README, the codebook and the
notes in `eda/`) are released under [CC BY 4.0](../LICENSE-docs.md). The ASAP-SAS item text, data table and
scoring-guide material reproduced in the codebook and prompt snapshots belong to their owners; see
[LICENSE-docs.md](../LICENSE-docs.md). To cite this work, use [CITATION.cff](../CITATION.cff).

## References

Hewlett Foundation (2012). *The Hewlett Foundation: Short Answer Scoring* [Data set and competition]. Kaggle.
https://www.kaggle.com/c/asap-sas

Williamson, D. M., Xi, X., & Breyer, F. J. (2012). A framework for evaluation and use of automated scoring.
*Educational Measurement: Issues and Practice, 31*(1), 2–13. https://doi.org/10.1111/j.1745-3992.2011.00223.x
