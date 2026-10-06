"""Step 4: codebook v0.1 rules (set1/score_from_codes.py) on dev codes, before and after the §3 recode.

Both are FITTED on dev (codes refined after seeing scores): optimistic estimates, not results.
  v1 codes   dev_codes_v1.csv mapped to v0.1 codes without the §3 overrides
  v0.1 codes dev_codes_v01.csv
Reported on all dev and excluding responses flagged `unfinished`.
"""
import sys

import pandas as pd

sys.path.insert(0, '.')
from common.evaluate import report
from set1.score_from_codes import score

sys.stdout.reconfigure(encoding='utf-8')
dev = pd.read_csv('data/set1/dev.csv')
v01 = pd.read_csv('set1/eda/dev_codes_v01.csv', dtype={'other': str, 'flags': str, 'note': str}).fillna('')
o = pd.read_csv('set1/eda/dev_overrides_v01.csv', dtype={'old': str, 'new': str}).fillna('')
pre = v01.set_index('Id').copy()
for r in o.itertuples():  # undo the §3 overrides
    pre.at[r.Id, r.column] = r.old if r.column == 'flags' else int(r.old)
d = dev.merge(v01, on='Id', validate='one_to_one')
d['v01'] = [score(r) for r in d.to_dict('records')]
d['pre'] = [score(pre.loc[i]) for i in d.Id]
d['unfinished'] = d['flags'].str.contains('unfinished')

for name, x in (('all dev', d), ('excluding unfinished', d[~d.unfinished])):
    print(f'== {name} (n={len(x)}) ==')
    print(pd.DataFrame([report(x.Score1, x.Score2, 'Score2 (human)'),
                        report(x.Score1, x.pre, 'v0.1 rules, codes before §3 recode'),
                        report(x.Score1, x.v01, 'v0.1 rules, v0.1 codes')]).to_string(index=False))
ch = d[d.pre != d.v01]
print(f'\nScores changed by the §3 recode: {len(ch)} | closer to Score1: {int(((ch.v01 - ch.Score1).abs() < (ch.pre - ch.Score1).abs()).sum())}'
      f', further: {int(((ch.v01 - ch.Score1).abs() > (ch.pre - ch.Score1).abs()).sum())}')
print(ch[['Id', 'Score1', 'Score2', 'pre', 'v01']].to_string(index=False))
