"""Step 12: the pre-registered test report (set1/eda/prereg_cv.md §7). Written before the test results were seen.

Inputs: set1/results/test_v0.2.jsonl (the single coding run), set1/results/cv_selected_config.json (frozen),
set1/results/baselines_test_predictions.csv (common/baselines.py --set 1 --test; fit on all train).
  Primary: best guess. Secondary: cross-validation-selected. QWK with 95% bootstrap CI, exact, SMD, degradation
  against human-human QWK (train, 0.944). Baselines: bag-of-words, length-only.
  Paired bootstrap: best guess - bag-of-words; selected - best guess.
  All of the above with and without responses the model flags `unfinished`.
  Routing (descriptive): responses whose best-guess score depends on a borderline call; agreement on the rest.
"""
import json
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, '.')
sys.path.insert(0, 'set1/eda')
from common.evaluate import paired_qwk_diff_ci, report
from step7_cv import BEST, GROUPS, scores

sys.stdout.reconfigure(encoding='utf-8')
HH = 0.944  # human-human QWK on train (Score2 vs Score1), set1/eda/step1_scores_agreement.py

recs = [json.loads(l) for l in open('set1/results/test_v0.2.jsonl', encoding='utf-8')]
errors = [r for r in recs if 'error' in r]
m = pd.DataFrame([r for r in recs if 'error' not in r]).drop(columns='split')
test = pd.read_csv('data/set1/test.csv')
m = m.merge(test, on='Id', validate='one_to_one').reset_index(drop=True)
print(f'test responses {len(test)} | coded {len(m)} | error records {len(errors)} | prompt hashes {set(m.prompt_hash)}')

L = {c: m[c].astype(int).to_numpy() for codes in GROUPS.values() for c in codes}
selected = json.load(open('set1/results/cv_selected_config.json'))
m['best'] = scores(L, BEST)
m['selected'] = scores(L, selected)
m['strict'] = scores(L, {**BEST, 'pooled_borderline': 'present'})
b = pd.read_csv('set1/results/baselines_test_predictions.csv').rename(
    columns={'bag-of-words (raw text)': 'bow', 'length-only': 'length'})
m = m.merge(b[['Id', 'bow', 'length']], on='Id', validate='one_to_one')
m['unf'] = m['flags'].map(lambda f: 'unfinished' in f)
print(f'unfinished (model flag): {int(m.unf.sum())} ({m.unf.mean():.1%})')

for name, x in (('all test', m), ('without unfinished', m[~m.unf])):
    y = x.Score1
    print(f'\n== {name} (n={len(x)}) ==')
    print(pd.DataFrame([report(y, x.best, 'PRIMARY best guess', HH), report(y, x.selected, 'SECONDARY CV-selected', HH),
                        report(y, x.bow, 'bag-of-words (fit on train)', HH), report(y, x.length, 'length-only (fit on train)', HH)]
                       ).to_string(index=False))
    for label, a, c in (('best guess - bag-of-words', x.best, x.bow), ('CV-selected - best guess', x.selected, x.best)):
        d, lo, hi = paired_qwk_diff_ci(y, a, c)
        print(f'  {label}: {d:+.4f} [{lo:+.4f}, {hi:+.4f}]')
    print('  confusion, best guess (rows Score1):')
    print(pd.crosstab(y, x.best).to_string())

dep = m.best != m.strict
rest = m[~dep]
print(f'\n== Routing (descriptive): best-guess score depends on a borderline call: {int(dep.sum())} ({dep.mean():.1%}) ==')
print(pd.DataFrame([report(m.Score1[dep], m.best[dep], 'routed (borderline-dependent)'),
                    report(rest.Score1, rest.best, 'not routed')]).to_string(index=False))
