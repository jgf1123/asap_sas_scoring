"""Test: responses where FULL >> C1 mattered (U=1 but full credit), split by human score. Prints text (local only)."""
import sys

import pandas as pd

sys.path.insert(0, '.')
from common.evaluate import load_run
from set10.score_from_codes import score

m = load_run('set10/results/test_v1.2.jsonl').merge(pd.read_csv('data/set10/test.csv'), on='Id')
m['group'] = m.text.str.split('::').str[0].str.contains('gray').map({True: 'gray', False: 'white/black'})
cfg = dict(zip(['B1', 'B2', 'B3', 'B4', 'B5', 'B6'], 'bbbbbb'))
m['b'] = [score(r, cfg) for r in m.to_dict('records')]
x = m[(m.U == 1) & (m.b == 2)]
print('U=1 but full credit (FULL >> C1 decided):', x.Score1.value_counts().sort_index().to_dict())
for r in x.sort_values('Score1').itertuples():
    print(f'\n{r.Id} human {r.Score1} | E{r.E} D{r.D} N{r.N} P{r.P} | {r.text[:230]}')
