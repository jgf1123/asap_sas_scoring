"""Step 2d: rater disagreements as residuals from a reference count.

c = min(3, rubric codes without AMT + 1 if any environment item (temperature/light/storage conditions)
          + 1 if cover containers)   -- what agreed dev cases credit; environment counted once (conservative).
c is fitted on dev: a lens for reading disagreements, not a scoring rule.
r1 = Score1 - c, r2 = Score2 - c. Each disagreement is typed by its residual pair:
  adds      one rater at c (0), the other above
  withholds one rater at c (0), the other below
  straddles one above, one below
  both off  both residuals nonzero, same sign (count misses something, or coding error)
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
CREDITED = ['VA', 'VT', 'MAT', 'SIZE', 'RT', 'DRY', 'CS', 'CT']
ENV = {'temperature', 'light', 'storage conditions'}
c = pd.read_csv('set1/eda/dev_codes_v1.csv', dtype={'other': str, 'flags': str, 'note': str}).fillna('')
d = c.merge(pd.read_csv('data/set1/dev.csv', usecols=['Id', 'Score1', 'Score2']), on='Id', validate='one_to_one')
labels = d.other.map(lambda s: {o.strip() for o in s.split(';') if o.strip()})
d['env'] = labels.map(lambda s: int(bool(s & ENV)))
d['cover'] = labels.map(lambda s: int('cover containers' in s))
d['c'] = (d[CREDITED].sum(axis=1) + d.env + d.cover).clip(upper=3)
d['r1'], d['r2'] = d.Score1 - d.c, d.Score2 - d.c

print(f'== All dev (n={len(d)}): residual distributions ==')
print(pd.DataFrame({'r1 (Score1 - c)': d.r1.value_counts().sort_index(), 'r2 (Score2 - c)': d.r2.value_counts().sort_index()}).fillna(0).astype(int).T.to_string())
print(f'exact agreement with c: Score1 {(d.r1 == 0).mean():.3f}, Score2 {(d.r2 == 0).mean():.3f}'
      f' | Score1 vs Score2 {(d.Score1 == d.Score2).mean():.3f}')
agree = d[d.Score1 == d.Score2]
print(f'when raters agree (n={len(agree)}): c matches {(agree.r1 == 0).mean():.3f}, above {(agree.r1 > 0).mean():.3f} (c too low), below {(agree.r1 < 0).mean():.3f} (c too high)')


def kind(r):
    a, b = r.r1, r.r2
    if a == 0 or b == 0:
        other = b if a == 0 else a
        return 'adds' if other > 0 else 'withholds'
    return 'straddles' if a * b < 0 else 'both off'


x = d[d.Score1 != d.Score2].copy()
x['type'] = x.apply(kind, axis=1)
x['deviant'] = x.apply(lambda r: 'Score1' if r.r2 == 0 else ('Score2' if r.r1 == 0 else '-'), axis=1)
print(f'\n== Disagreements (n={len(x)}) by type and by which rater departs from c ==')
print(pd.crosstab(x.type, x.deviant, margins=True, margins_name='total').to_string())

CODES = CREDITED + ['AMT']
for t, g in x.groupby('type'):
    print(f'\n-- {t} (n={len(g)}) --')
    for r in g.sort_values('Id').to_dict('records'):
        codes = ','.join(k for k in CODES if r[k]) or '-'
        print(f'  {r["Id"]:5d} c={r["c"]} r1={r["r1"]:+d} r2={r["r2"]:+d} | {codes} | other: {r["other"] or "-"} | flags: {r["flags"] or "-"}')
