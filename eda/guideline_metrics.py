"""Williamson, Xi & Breyer (2012) style metrics on test: QWK and Pearson r (each vs human-human on train),
and the discrepancy rate (|difference| = 2 on the 0-2 scale, which would trigger adjudication)."""
import sys

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

sys.path.insert(0, '.')
from evaluate import load_run, qwk
from score_from_codes import score

train = pd.concat([pd.read_csv('data/set10/dev.csv'), pd.read_csv('data/set10/remainder.csv')])
hh_q, hh_r = qwk(train.Score1, train.Score2), pearsonr(train.Score1, train.Score2).statistic
hh_disc = (abs(train.Score1 - train.Score2) == 2).mean()

m = load_run('results/test_v1.2.jsonl').merge(pd.read_csv('data/set10/test.csv'), on='Id')
m['group'] = m.text.str.split('::').str[0].str.contains('gray').map({True: 'gray', False: 'white/black'})
for name, c in (('LLM all-b (pre-registered)', 'bbbbbb'), ('LLM all-a', 'aaaaaa')):
    m[name] = [score(r, dict(zip(['B1', 'B2', 'B3', 'B4', 'B5', 'B6'], c))) for r in m.to_dict('records')]
base = pd.read_csv('results/baselines_test_predictions.csv')
m = m.merge(base.rename(columns={'bag-of-words (wraps repaired)': 'bag-of-words'})[['Id', 'bag-of-words']], on='Id')

rows = [{'scorer': 'human-human (train, n=1640)', 'QWK': hh_q, 'r': hh_r, 'disc. rate': hh_disc}]
for n in ('LLM all-b (pre-registered)', 'LLM all-a', 'bag-of-words'):
    rows.append({'scorer': n, 'QWK': qwk(m.Score1, m[n]), 'r': pearsonr(m.Score1, m[n]).statistic,
                 'disc. rate': (abs(m.Score1 - m[n]) == 2).mean()})
t = pd.DataFrame(rows)
t['QWK degr.'], t['r degr.'] = hh_q - t.QWK, hh_r - t.r
print(t.round(3).to_string(index=False))
print(f'discrepant counts on test: ' + ', '.join(f'{n}: {int((abs(m.Score1 - m[n]) == 2).sum())}' for n in ('LLM all-b (pre-registered)', 'LLM all-a', 'bag-of-words')))
