"""Pre-registered test analysis (eda/prereg_remainder.md): selected config (all-b) and all-a, plus baselines.

Test has a single human score (Score1); degradation uses human-human QWK on Set 10 train (Score1 vs Score2).
Run after the single LLM test run and `python baselines.py --test`.
"""
import sys

import pandas as pd

sys.path.insert(0, '.')
from evaluate import load_run, qwk, report
from score_from_codes import score

RULES = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']
raw = [l for l in open('results/test_v1.2.jsonl', encoding='utf-8')]
r = load_run('results/test_v1.2.jsonl')
assert len(raw) == len(r) == 546 and set(r.prompt_hash) == {'34e06a141c41'}, 'test run incomplete or wrong prompt'

test = pd.read_csv('data/set10/test.csv')
m = r.merge(test, on='Id')
m['group'] = m.text.str.split('::').str[0].str.contains('gray').map({True: 'gray', False: 'white/black'})
for name, c in (('all-b', 'bbbbbb'), ('all-a', 'aaaaaa')):
    cfg = dict(zip(RULES, c))
    m[name] = [score(row, cfg) for row in m.to_dict('records')]

train = pd.concat([pd.read_csv('data/set10/dev.csv'), pd.read_csv('data/set10/remainder.csv')])
hh = qwk(train.Score1, train.Score2)
base = pd.read_csv('results/baselines_test_predictions.csv').merge(test[['Id', 'Score1']], on='Id')

rows = [report(m.Score1, m['all-b'], 'LLM codes -> rules, all-b (selected)', hh),
        report(m.Score1, m['all-a'], 'LLM codes -> rules, all-a', hh),
        report(m.Score1, m.score, 'LLM own score (prompt all-a)', hh),
        report(base.Score1, base['bag-of-words (wraps repaired)'], 'bag-of-words, wraps repaired', hh),
        report(base.Score1, base['bag-of-words (raw text)'], 'bag-of-words, raw text', hh),
        report(base.Score1, base['length-only'], 'length-only', hh)]
print(f'Test set: n={len(m)} | human-human QWK reference (train): {hh:.3f}')
print(pd.DataFrame(rows).to_string(index=False))
for n in ('all-b', 'all-a'):
    print(f'\nConfusion {n} (rows Score1):'); print(pd.crosstab(m.Score1, m[n]))

# Exploratory (not pre-registered): paired bootstrap, LLM configs vs the bag-of-words baseline on test.
from evaluate import paired_qwk_diff_ci
mb = m.merge(base[['Id', 'bag-of-words (wraps repaired)']], on='Id')
print('\nExploratory paired comparisons on test:')
for n in ('all-b', 'all-a'):
    d, lo, hi = paired_qwk_diff_ci(mb.Score1, mb[n], mb['bag-of-words (wraps repaired)'])
    print(f'  QWK(LLM {n}) - QWK(bag-of-words) = {d:+.3f}, paired 95% CI [{lo:+.3f}, {hi:+.3f}]')
d, lo, hi = paired_qwk_diff_ci(m.Score1, m['all-b'], m['all-a'])
print(f'  QWK(all-b) - QWK(all-a) = {d:+.3f}, paired 95% CI [{lo:+.3f}, {hi:+.3f}]')
