"""Step 2c: dev responses where Score1 != Score2, with v1 codes, grouped by boundary.

p = min(3, rubric codes incl. AMT); p_noAMT = the same without AMT. Prints text, to look for items that one
rater credits and the other does not (patterns across cases, not explanations of single cases).
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
CODES = ['VA', 'VT', 'MAT', 'SIZE', 'AMT', 'RT', 'DRY', 'CS', 'CT']
c = pd.read_csv('set1/eda/dev_codes_v1.csv', dtype={'other': str, 'flags': str, 'note': str}).fillna('')
d = c.merge(pd.read_csv('data/set1/dev.csv'), on='Id', validate='one_to_one')
d['p'] = d[CODES].sum(axis=1).clip(upper=3)
d['p_noAMT'] = d[[k for k in CODES if k != 'AMT']].sum(axis=1).clip(upper=3)
x = d[d.Score1 != d.Score2].copy()
x['lo'], x['hi'] = x[['Score1', 'Score2']].min(axis=1), x[['Score1', 'Score2']].max(axis=1)
x['boundary'] = x.lo.astype(str) + '/' + x.hi.astype(str)
print(f'{len(x)} disagreements | by boundary: {x.boundary.value_counts().sort_index().to_dict()}'
      f' | Score1 higher {int((x.Score1 > x.Score2).sum())}, Score2 higher {int((x.Score2 > x.Score1).sum())}')
for b, g in x.sort_values(['boundary', 'Id']).groupby('boundary', sort=False):
    print(f'\n===== {b} (n={len(g)}) =====')
    for r in g.to_dict('records'):
        codes = ','.join(k for k in CODES if r[k]) or '-'
        print(f'{r["Id"]}  S1={r["Score1"]} S2={r["Score2"]}  p={r["p"]} p_noAMT={r["p_noAMT"]} | {codes}'
              f' | other: {r["other"] or "-"} | flags: {r["flags"] or "-"}')
        print(f'    {r["text"].replace("^p", " ⏎ ")}')
