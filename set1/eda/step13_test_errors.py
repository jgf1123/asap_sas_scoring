"""Step 13: error analysis of the primary (best-guess) test scores. Descriptive only: the test set is spent, and
nothing here changes the codebook or rules. Test has Score1 only, so model error and rater idiosyncrasy cannot
be told apart.

Each disagreement (best guess != Score1) gets the first cause that applies:
  1 truncation          flagged `unfinished` by the model
  2 borderline credit   counting borderline calls moved the score away from Score1 (strict is closer)
  3 contested item      model below Score1, and crediting one uncredited group present or borderline
                        (MATV, AMT, MATK, MASS, RINSE, DESIGN) would reach Score1
  4 over-credit         model above Score1 with clearly present credited codes (the human gave less)
  5 under-credit        model below Score1, no code explains it
Then prints the large errors (|diff| >= 2) and, with --all, every disagreement.
"""
import json
import sys
from collections import Counter

import numpy as np
import pandas as pd

sys.path.insert(0, 'set1/eda')
from step7_cv import BEST, GROUPS, scores

sys.stdout.reconfigure(encoding='utf-8')
UNCREDITED = ['MATV', 'AMT', 'MATK', 'MASS', 'RINSE', 'DESIGN']

recs = [json.loads(l) for l in open('set1/results/test_v0.2.jsonl', encoding='utf-8')]
m = pd.DataFrame(recs).drop(columns='split').merge(pd.read_csv('data/set1/test.csv'), on='Id').reset_index(drop=True)
L = {c: m[c].astype(int).to_numpy() for codes in GROUPS.values() for c in codes}
best = scores(L, BEST)
strict = scores(L, {**BEST, 'pooled_borderline': 'present'})
credit = {g: scores(L, {**BEST, g: 'borderline'}) for g in UNCREDITED}
y = m.Score1.to_numpy()
unf = m['flags'].map(lambda f: 'unfinished' in f).to_numpy()

cause, detail = [], []
for i in range(len(m)):
    if best[i] == y[i]:
        cause.append(''); detail.append(''); continue
    if unf[i]:
        cause.append('1 truncation'); detail.append(''); continue
    if abs(strict[i] - y[i]) < abs(best[i] - y[i]):
        cause.append('2 borderline credit')
        detail.append(','.join(e['code'] + f'({e["reason"]})' for e in m.at[i, 'borderline'])); continue
    if best[i] < y[i]:
        hits = [g for g in UNCREDITED if credit[g][i] == y[i]]
        if hits:
            cause.append('3 contested item'); detail.append(','.join(hits)); continue
        cause.append('5 under-credit'); detail.append(''); continue
    cause.append('4 over-credit'); detail.append('')
m['best'], m['strict'], m['cause'], m['detail'] = best, strict, cause, detail
x = m[m.cause != '']

print(f'test n={len(m)} | disagreements {len(x)} | model above Score1 {int((x.best > x.Score1).sum())}, below {int((x.best < x.Score1).sum())}')
print(pd.crosstab(x.cause, np.where(x.best > x.Score1, 'model above', 'model below'), margins=True).to_string())
for c in ('2 borderline credit', '3 contested item'):
    g = x[x.cause == c]
    items = Counter(t.split('(')[0] for d in g.detail for t in d.split(',') if t)
    reasons = Counter(t.split('(')[1].rstrip(')') for d in g.detail for t in d.split(',') if '(' in t)
    print(f'{c}: codes {dict(items.most_common())}' + (f' | reasons {dict(sorted(reasons.items()))}' if reasons else ''))
print('by boundary (min/max):', (x[['best', 'Score1']].min(axis=1).astype(str) + '/' + x[['best', 'Score1']].max(axis=1).astype(str)).value_counts().sort_index().to_dict())


def show(r):
    pres = ','.join(c for c in L if r[c] == 2) or '-'
    print(f'{r.Id} Score1={r.Score1} model={r.best} strict={r.strict} | {r.cause} {r.detail} | present: {pres}'
          f' | other: {r["other"]} | flags: {r["flags"]}')
    print(f'    {r.text.replace("^p", " / ")}')
    for e in r['borderline']:
        print(f'    [{e["code"]} ({e["reason"]})] {e["note"]}')
    print(f'    rationale: {r.rationale}')


print('\n== Large errors (|model - Score1| >= 2) ==')
for _, r in x[(x.best - x.Score1).abs() >= 2].sort_values('Id').iterrows():
    show(r)
if '--all' in sys.argv:
    for c, g in x.groupby('cause'):
        print(f'\n== {c} (n={len(g)}) ==')
        for _, r in g.sort_values('Id').iterrows():
            show(r)
