# LLM Short-Answer Scoring with a Written Codebook (ASAP-SAS, Set 10)

Can a large language model score student short answers the way trained human raters do, given only a written codebook and no training labels? This project scores one science item from the ASAP Short Answer Scoring dataset with Claude Opus 5.5 and evaluates it against the official human scores using quadratic weighted kappa (QWK), the field-standard metric.

## Results (official test set, one pre-registered run, n = 546)

| Scorer | QWK [95% CI] | Exact | SMD |
|---|---|---|---|
| **LLM + codebook (pre-registered configuration)** | **0.763** [0.719, 0.805] | 0.80 | +0.07 |
| LLM + codebook (official-leaning configuration) | 0.775 [0.729, 0.817] | 0.79 | −0.08 |
| Bag-of-words logistic regression (trained on 1,640 labels) | 0.709 [0.653, 0.754] | 0.78 | +0.09 |
| Length-only | 0.457 [0.394, 0.516] | 0.62 | +0.07 |
| *Second human rater (train set reference)* | *0.884* | *0.89* | |

*Sections to be written: the item and data; codebook design; scoring pipeline; evaluation design (splits, pre-registration); prompt iterations (v1.0 → v1.2); error analysis; limitations.*

## What the rules contributed, and what that teaches

The codebook separates *what a response contains* (codes such as "states an effect on the doghouse" or "cites an experiment result") from *how codes become a score*. The scoring rules form a ranked list: the first rule whose condition holds decides the score. The rules come in tiers: **O**, the official rubric text; **C**, consensus rules describing what the two human raters did when they agreed; **B**, boundary rules for cases where raters disagreed, each with an official-leaning and a rater-leaning variant; and **S**, a candidate tendency of one rater. Because the LLM outputs codes, every rule set and ordering can be re-scored from one LLM run at no extra cost. The analysis below is exploratory: it was done after the test run and does not change the reported result. Numbers are for the remainder set (n = 1,340, the validation split), with the test set (n = 546) as replication.

**Tiers.** The official rubric alone, applied literally, reaches QWK 0.699 (test 0.692), below the 0.70 floor used in operational scoring. Adding the consensus rules raises this to 0.769 (test 0.791). Most of that gain comes from a single rule: counting "not too hot, not too cold" as a description of the effect for a gray paint choice. Adding the boundary rules *lowered* QWK (0.750; test 0.763), mostly through one rule that gave partial credit to general physics claims, which was wrong half the time it fired. The rater-specific rule lowered it sharply (0.630).

**Ordering.** Across all 5,040 orderings of the seven ranked rules, QWK ranged from 0.23 to 0.77, but only 72–169 distinct score patterns arose: most orderings are equivalent. Nearly all the variation came from one requirement: the full-credit rule must outrank the general partial-credit rules, the "specific before general" principle known in linguistics as the Elsewhere Condition. The one substantive ordering choice was whether a misconception should override an otherwise complete answer. Placing full credit first (rubric v1.2) was worth +0.029 QWK on the remainder and +0.038 on test, both with confidence intervals excluding zero. The best of all 5,040 orderings beat the one used by only about 0.01, within selection noise.

**The lesson.** Rules supported by many agreeing human decisions generalized to new data; rules written to resolve a handful of edge cases (3–7 examples each) did not, and as a group they made the scorer worse. In retrospect this is the familiar bias–variance trade-off applied to a codebook: each boundary rule was a parameter fit to a few development cases. A simpler codebook, official plus consensus rules only, scored best on both held-out sets. That conclusion was reached after seeing those sets, so it is a hypothesis for the next iteration rather than a result.

**Next iteration: cross-validate the rules themselves.** Because rules are applied to fixed LLM codes, rule sets and orderings can be selected inside k-fold cross-validation on the training data: choose rules and ranking on k−1 folds, score the held-out fold, and repeat. This gives an honest estimate of how much rule selection helps, and rules or ranking constraints chosen consistently across folds identify the key rules, a form of stability selection. Rules that come and go between folds are fitting noise. This would replace judging boundary rules by reading a few dozen development cases.

**A design flaw this exposed.** Two boundary rules changed a code rather than a score (for example, "a restated hypothesis does not count as a result"). Because the chosen variant was included in the LLM's prompt, the model applied it while coding, so the alternative variant could not be tested afterwards. In the next iteration the prompt should ask only for observations (codes and flags) and leave every scoring decision to the post-hoc rules.
