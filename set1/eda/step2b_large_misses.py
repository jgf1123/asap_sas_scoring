"""Step 2b: dev responses where the rubric-only score p misses Score1 by 2 or more points.

Prints text with blind codes and both scores, to separate coding errors, truncation and rater behavior.
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
CODES = ['VA', 'VT', 'MAT', 'SIZE', 'RT', 'DRY', 'CS', 'CT']
c = pd.read_csv('set1/eda/dev_codes.csv', dtype={'other': str, 'flags': str, 'note': str}).fillna('')
d = c.merge(pd.read_csv('data/set1/dev.csv'), on='Id', validate='one_to_one')
d['k'] = d[CODES].sum(axis=1)
d['p'] = d.k.clip(upper=3)
x = d[(d.p - d.Score1).abs() >= 2].sort_values(['p', 'Score1'])
print(f'{len(x)} responses with |p - Score1| >= 2\n')
for r in x.to_dict('records'):
    codes = ','.join(k for k in CODES if r[k]) or '-'
    print(f'{r["Id"]}  p={r["p"]}  Score1={r["Score1"]} Score2={r["Score2"]} | codes: {codes} | other: {r["other"] or "-"}'
          f' | flags: {r["flags"] or "-"}{" | note: " + r["note"] if r["note"] else ""}')
    print(f'    {r["text"].replace("^p", " ⏎ ")}\n')
