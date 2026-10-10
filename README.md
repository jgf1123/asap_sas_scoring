# LLM Short-Answer Scoring with a Written Codebook (ASAP-SAS)

Can a large language model score student short answers the way trained human raters do? This project scores science items from the [ASAP Short Answer Scoring](https://www.kaggle.com/c/asap-sas) dataset with Claude, working from a written codebook rather than labeled examples. For each item, a codebook is developed on a labeled development set, and the model records **codes** (what a response contains). Deterministic **rules** then turn those codes into a score. Scores are evaluated against the official human scores with quadratic weighted kappa (QWK), with configurations pre-registered before any held-out run.

## Items

| Set | Item | Status | Test QWK (pre-registered) | Human–human QWK |
|---|---|---|---|---|
| [10](set10/README.md) | "Doghouse", grade 8 science | Complete | 0.763 | 0.884 |
| [1](set1/README.md) | "Acid Rain", grade 10 science | Complete | 0.895 | 0.944 |

Set 10 came first because its scoring guide lists explicit components, its score distribution is balanced and its raters agree well. Set 1, the next balanced science item, applies the lessons from Set 10: the model records codes only, codes are recorded as present, borderline or absent, and every scoring rule is rated by cross-validation before a single pre-registered test run (see [set1/README.md](set1/README.md#what-changed-from-set-10)). The two items are not directly comparable: Set 1's rubric counts pieces of information, which maps naturally onto codes.

## Repository layout

```
score.py            scores responses with Claude: python score.py --set N ...
common/             set-independent code: data splits, evaluation metrics, baselines, text cleaning
eda/                dataset-wide exploration (label distributions and rater agreement across sets)
set10/, set1/       one folder per item:
  README.md           write-up
  rubric.md           codebook
  config.py           prompt, output schema and item-specific options used by score.py
  score_from_codes.py deterministic codes -> score rules
  eda/                exploration, pre-registrations and analysis scripts
  results/            prompt snapshots and model outputs
```

Run all commands from the repository root.

## Data

The ASAP-SAS data is available from the [Kaggle competition page](https://www.kaggle.com/c/asap-sas) after accepting the competition rules; see the page's Rules tab for the terms of use. It is not redistributed here. Place `train.tsv`, `public_leaderboard_rel_2.tsv` and `public_leaderboard_solution.csv` in `data/`, then build an item's splits with `pixi run python common/make_split.py N`. Model outputs, hand-coding files and reading lists quote student responses and are not included.

## License and citation

Code is released under the [MIT License](LICENSE). The written documents are released under [CC BY 4.0](LICENSE-docs.md). ASAP-SAS item text and scoring-guide material reproduced in the codebooks and prompt snapshots belong to their owners and are not covered by either license; see [LICENSE-docs.md](LICENSE-docs.md). To cite this work, use [CITATION.cff](CITATION.cff).
