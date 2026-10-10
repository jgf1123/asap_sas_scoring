"""Step 9 (exploratory, after the frozen pre-registration): do two partial items make one point?

All train responses (dev + remainder), model v0.2 codes. A "partial" is an item that earns no point by itself:
  D1  uncredited codes (MATV, AMT, MATK, MASS, RINSE, DESIGN) at present or borderline; base = best guess
  D2  D1 plus borderline calls on credited codes; base = strict scoring (only present counts)
For responses with base score < 3, residual = rater score - base, by number of partials (distinct groups).
Hypothesis "two partials = one point": residual ~0 at 0-1 partials, ~+1 at 2+.
Then the rule base + floor(partials / 2), capped at 3, against the best guess: QWK with paired bootstrap.
Reported with and without responses flagged `unfinished`.
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
recs = [json.loads(l) for p in ('set1/results/dev_v0.2.jsonl', 'set1/results/remainder_v0.2.jsonl')
        for l in open(p, encoding='utf-8')]
m = pd.DataFrame(recs).drop(columns='split')
m = m.merge(pd.concat([pd.read_csv(f'data/set1/{s}.csv') for s in ('dev', 'remainder')]), on='Id').reset_index(drop=True)
L = {c: m[c].astype(int).to_numpy() for codes in GROUPS.values() for c in codes}
unf = m['flags'].map(lambda f: 'unfinished' in f).to_numpy()
UNCREDITED = ['MATV', 'AMT', 'MATK', 'MASS', 'RINSE', 'DESIGN']
CREDITED = [g for g in GROUPS if g not in UNCREDITED]


def any_level(g, k):
    return np.any([L[c] >= k for c in GROUPS[g]], axis=0)


p1 = np.sum([any_level(g, 1) for g in UNCREDITED], axis=0)
borderline_only = [any_level(g, 1) & ~any_level(g, 2) for g in CREDITED]
p2 = p1 + np.sum(borderline_only, axis=0)
best = scores(L, BEST)
strict = scores(L, {**BEST, 'pooled_borderline': 'present'})
y1, y2 = m.Score1.to_numpy(), m.Score2.to_numpy()
agree = y1 == y2

for name, base, p in (('D1: uncredited codes; base = best guess', best, p1),
                      ('D2: uncredited codes + borderline calls; base = strict', strict, p2)):
    for label, keep in (('all', np.ones(len(m), bool)), ('without unfinished', ~unf)):
        k = keep & (base < 3)
        rows = []
        for n in range(4):
            s = k & (np.minimum(p, 3) == n)
            if s.sum() == 0:
                continue
            a = s & agree
            rows.append({'partials': f'{n}+' if n == 3 else n, 'n': int(s.sum()),
                         'mean resid Score1': round((y1[s] - base[s]).mean(), 2),
                         'mean resid Score2': round((y2[s] - base[s]).mean(), 2),
                         'agreed n': int(a.sum()), 'agreed mean resid': round((y1[a] - base[a]).mean(), 2),
                         'agreed % resid >= 1': round(100 * ((y1[a] - base[a]) >= 1).mean())})
        print(f'\n== {name} | {label} (base score < 3) ==')
        print(pd.DataFrame(rows).to_string(index=False))

print('\n== Rule "base + floor(partials / 2)", capped at 3, vs best guess (all train, Score1) ==')
for name, base, p in (('D1', best, p1), ('D2', strict, p2)):
    rule = np.minimum(base + p // 2, 3)
    for label, keep in (('all', np.ones(len(m), bool)), ('without unfinished', ~unf)):
        d, lo, hi = paired_qwk_diff_ci(y1[keep], rule[keep], best[keep])
        r = report(y1[keep], rule[keep], f'{name} rule')
        print(f'{name} {label:19s}: QWK {r["QWK"]} exact {r["exact"]} SMD {r["SMD"]} | minus best guess {d:+.4f} [{lo:+.4f}, {hi:+.4f}]'
              f' | responses changed {int((rule[keep] != best[keep]).sum())}')
