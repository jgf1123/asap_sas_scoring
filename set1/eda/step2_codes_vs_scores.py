"""Step 2: blind dev codes vs scores. Which pieces of information did the raters credit?

p = min(3, number of distinct rubric codes), CS and CT counted separately (the rubric-only score).
A. p vs Score1: confusion, exact agreement, QWK.
B. "other" labels: among responses with p <= 2 (room for one more credited piece), residual = score - p.
   A credited item should push residuals to +1; an uncredited one should look like the reference row
   (responses with no "other" label).
C. Rubric codes, leave-one-out: residual = score - min(3, k - code) among responses with the code and
   k - code <= 2. A credited code should give residuals near +1.
Residuals are shown for Score1 and Score2. They also absorb coding errors; small n is anecdote.
D. As C, restricted to responses where Score1 == Score2 (the cases we can be most certain about).

Usage: python set1/eda/step2_codes_vs_scores.py [codes file]   (default: blind dev_codes.csv)
"""
import sys

import pandas as pd

sys.path.insert(0, '.')
from common.evaluate import qwk

sys.stdout.reconfigure(encoding='utf-8')
path = sys.argv[1] if len(sys.argv) > 1 else 'set1/eda/dev_codes.csv'
c = pd.read_csv(path, dtype={'other': str, 'flags': str, 'note': str}).fillna('')
CODES = [k for k in ['VA', 'VT', 'MAT', 'SIZE', 'AMT', 'RT', 'DRY', 'CS', 'CT'] if k in c]
print(f'codes file: {path} | rubric codes: {CODES}')
d = c.merge(pd.read_csv('data/set1/dev.csv', usecols=['Id', 'Score1', 'Score2']), on='Id', validate='one_to_one')
d['k'] = d[CODES].sum(axis=1)
d['p'] = d.k.clip(upper=3)
d['labels'] = d.other.map(lambda s: {o.strip() for o in s.split(';') if o.strip()})

print(f'== A. Rubric-only score p vs Score1 (dev n={len(d)}) ==')
print(pd.crosstab(d.p, d.Score1, rownames=['p'], margins=True, margins_name='total').to_string())
print(f'exact {(d.p == d.Score1).mean():.3f} | QWK {qwk(d.Score1, d.p):.3f}'
      f' | p below Score1 {int((d.p < d.Score1).sum())}, above {int((d.p > d.Score1).sum())}'
      f' | (Score2 vs Score1: exact {(d.Score2 == d.Score1).mean():.3f}, QWK {qwk(d.Score1, d.Score2):.3f})')


def summarize(name, x, base):
    r1, r2 = x.Score1 - base, x.Score2 - base
    return {'item': name, 'n': len(x), 'mean r1': round(r1.mean(), 2), '% r1>0': round(100 * (r1 > 0).mean()),
            '% r1=0': round(100 * (r1 == 0).mean()), '% r1<0': round(100 * (r1 < 0).mean()), 'mean r2': round(r2.mean(), 2)}


print('\n== B. "other" labels, responses with p <= 2 (residual = score - p) ==')
room = d[d.p <= 2]
rows = [summarize('(reference: no "other" label)', room[room.labels.map(len) == 0], room[room.labels.map(len) == 0].p)]
counts = pd.Series([l for s in room.labels for l in s]).value_counts()
for lab, n in counts.items():
    if n >= 3:
        x = room[room.labels.map(lambda s: lab in s)]
        rows.append(summarize(lab, x, x.p))
print(pd.DataFrame(rows).to_string(index=False))
print(f'(labels with n < 3 in this subset omitted: {", ".join(f"{k} {v}" for k, v in counts[counts < 3].items())})')

for title, sub in (('C. Rubric codes, leave-one-out (residual = score - min(3, k - code))', d),
                   ('D. As C, raters agree (Score1 == Score2)', d[d.Score1 == d.Score2])):
    print(f'\n== {title}, n={len(sub)} ==')
    rows = []
    for code in CODES:
        x = sub[(sub[code] == 1) & (sub.k - sub[code] <= 2)]
        rows.append(summarize(code, x, (x.k - x[code]).clip(upper=3)))
    print(pd.DataFrame(rows).to_string(index=False))
