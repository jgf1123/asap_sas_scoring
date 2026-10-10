"""Step 11 (exploratory): how often raters accept each code group when it is present vs only borderline.

For each group: responses where the group's highest level is 2 (present) or 1 (borderline only). Base = best-guess
score with that group switched off; keep responses with base < 3 (room for a point). Residual = rater score - base.
About +1 = accepted, about 0 = not. Agreed cases (Score1 == Score2) are the main view; all train and the
remainder alone. Source of each group: rubric list, anchor papers, or discovered from responses.
"""
import json
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, 'set1/eda')
from step7_cv import BEST, GROUPS, scores

sys.stdout.reconfigure(encoding='utf-8')
SOURCE = {**{g: 'rubric' for g in ['VA', 'VT', 'MAT', 'SIZE', 'RT', 'DRY', 'container']},
          'COVER': 'anchor', 'MASS': 'anchor',
          **{g: 'discovered' for g in ['surroundings', 'MATV', 'AMT', 'MATK', 'RINSE', 'DESIGN']}}

runs = ['set1/results/dev_v0.2.jsonl', 'set1/results/remainder_v0.2.jsonl']
m = pd.DataFrame([json.loads(l) for p in runs for l in open(p, encoding='utf-8')]).drop(columns='split')
m = m.merge(pd.concat([pd.read_csv(f'data/set1/{s}.csv').assign(split=s) for s in ('dev', 'remainder')]),
            on='Id').reset_index(drop=True)
L = {c: m[c].astype(int).to_numpy() for codes in GROUPS.values() for c in codes}
y = m.Score1.to_numpy()
agree = (m.Score1 == m.Score2).to_numpy()

for name, keep in (('all train', np.ones(len(m), bool)), ('remainder only', (m.split == 'remainder').to_numpy())):
    rows = []
    for g in SOURCE:
        level = np.max([L[c] for c in GROUPS[g]], axis=0)
        base = scores(L, {**BEST, g: 'off'})
        for lv, lab in ((2, 'present'), (1, 'borderline')):
            s = keep & agree & (level == lv) & (base < 3)
            r = y[s] - base[s]
            rows.append({'group': g, 'source': SOURCE[g], 'level': lab, 'n agreed': int(s.sum()),
                         'mean residual': round(r.mean(), 2) if s.sum() else None,
                         '% accepted (resid >= 1)': round(100 * (r >= 1).mean()) if s.sum() else None})
    t = pd.DataFrame(rows)
    w = t.pivot(index=['source', 'group'], columns='level', values=['n agreed', 'mean residual', '% accepted (resid >= 1)'])
    w = w.reindex(['present', 'borderline'], axis=1, level=1)
    print(f'\n== {name}: agreed cases ==')
    print(w.sort_index(level=0, key=lambda i: i.map({'rubric': 0, 'anchor': 1, 'discovered': 2})).to_string())
