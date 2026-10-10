"""Step 8 (exploratory, after the frozen pre-registration): rater disagreements in the remainder.

Model v0.2 codes, best-guess configuration (set1/eda/step7_cv.py BEST). Test configurations are frozen; nothing
here changes them.
1. Overview: disagreements by boundary and direction; `unfinished` share.
2. Where the model's score sits: lower rater / higher rater / neither.
3. Single-code bridges. Model at the lower rater: which one code, credited (an uncredited code at either level,
   or a credited code's borderline call when not counted), would raise the score to the higher rater.
   Model at the higher rater: which one credited code, removed, would lower it to the lower rater.
   Reference: among AGREED responses, how often the same change would move the score away from the raters.
4. "other" items in disagreements no single code explains; a few texts per pattern.
"""
import json
import sys
from collections import Counter

import numpy as np
import pandas as pd

sys.path.insert(0, 'set1/eda')
from step7_cv import BEST, GROUPS, scores

sys.stdout.reconfigure(encoding='utf-8')
SAMPLE = int(sys.argv[1]) if len(sys.argv) > 1 else 3

m = pd.DataFrame([json.loads(l) for l in open('set1/results/remainder_v0.2.jsonl', encoding='utf-8')])
m = m.drop(columns='split').merge(pd.read_csv('data/set1/remainder.csv'), on='Id').reset_index(drop=True)
L = {c: m[c].astype(int).to_numpy() for codes in GROUPS.values() for c in codes}
s = scores(L, BEST)
m['s'] = s
m['unf'] = m['flags'].map(lambda f: 'unfinished' in f)
dis = (m.Score1 != m.Score2).to_numpy()
m['lo'], m['hi'] = m[['Score1', 'Score2']].min(axis=1), m[['Score1', 'Score2']].max(axis=1)

print(f'== 1. Remainder n={len(m)}: disagreements {int(dis.sum())} ({dis.mean():.1%}) ==')
x = m[dis]
print('boundary:', (x.lo.astype(str) + '/' + x.hi.astype(str)).value_counts().sort_index().to_dict(),
      '| Score1 higher', int((x.Score1 > x.Score2).sum()), '| Score2 higher', int((x.Score2 > x.Score1).sum()))
print(f'unfinished: disagreements {int(x.unf.sum())}/{len(x)} ({x.unf.mean():.1%}), agreements {int(m[~dis].unf.sum())}/{int((~dis).sum())} ({m[~dis].unf.mean():.1%})')

pos = np.where(s == m.lo, 'model at lower rater', np.where(s == m.hi, 'model at higher rater', 'model at neither'))
m['pos'] = pos
print('\n== 2. Where the best-guess score sits ==')
print(m[dis].pos.value_counts().to_string())

# Single-code changes. For "add": groups set to borderline (credits present or borderline). For "remove": group off.
adds = {}
for g in GROUPS:
    if BEST[g] != 'borderline':
        adds[g] = scores(L, {**BEST, g: 'borderline'})
removes = {g: scores(L, {**BEST, g: 'off'}) for g in GROUPS if BEST[g] != 'off'}
y1 = m.Score1.to_numpy()
agree = ~dis

rows, explained = [], np.zeros(len(m), bool)
low = (pos == 'model at lower rater') & dis
high = (pos == 'model at higher rater') & dis
for g, sg in adds.items():
    bridge = low & (sg == m.hi.to_numpy())
    spoil = agree & (sg != s) & (s == y1)  # agreed and correct now, wrong after
    fix = agree & (sg != s) & (sg == y1)
    explained |= bridge
    rows.append({'change': f'credit {g}', 'bridges (model at lower)': int(bridge.sum()),
                 'agreed: would spoil': int(spoil.sum()), 'agreed: would fix': int(fix.sum())})
for g, sg in removes.items():
    bridge = high & (sg == m.lo.to_numpy())
    spoil = agree & (sg != s) & (s == y1)
    fix = agree & (sg != s) & (sg == y1)
    explained |= bridge
    rows.append({'change': f'remove {g}', 'bridges (model at higher)': int(bridge.sum()),
                 'agreed: would spoil': int(spoil.sum()), 'agreed: would fix': int(fix.sum())})
t = pd.DataFrame(rows).fillna(0)
for c in ('bridges (model at lower)', 'bridges (model at higher)'):
    t[c] = t[c].astype(int)
t['bridges'] = t['bridges (model at lower)'] + t['bridges (model at higher)']
print('\n== 3. Single-code changes that would close the gap (and their effect on agreed responses) ==')
print(t[t.bridges + t['agreed: would spoil'] > 0].sort_values('bridges', ascending=False)
      [['change', 'bridges', 'agreed: would spoil', 'agreed: would fix']].to_string(index=False))
for name, mask in (('model at lower', low), ('model at higher', high)):
    print(f'{name}: {int(mask.sum())}, explained by a single code {int((mask & explained).sum())}')

un = dis & ~explained
print(f'\n== 4. Disagreements no single code explains: {int(un.sum())} (unfinished among them: {int(m.unf[un].sum())}) ==')
oth = Counter(o.lower() for lst in m.loc[un, 'other'] for o in lst)
print('most common "other" items:', dict(oth.most_common(12)))
print('flags:', dict(Counter(f for lst in m.loc[un, 'flags'] for f in lst)))
print(f'\nSample texts (up to {SAMPLE} per position):')
for p, g in m[un].groupby('pos'):
    for _, r in g.head(SAMPLE).iterrows():
        pres = ','.join(c for c in L if r[c] == 2) or '-'
        print(f'  [{p}] {r.Id} S1={r.Score1} S2={r.Score2} model={r.s} | present: {pres} | other: {r["other"]} | flags: {r["flags"]}')
        print(f'      {r.text.replace("^p", " / ")[:300]}')
