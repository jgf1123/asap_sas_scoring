"""Step 10 (exploratory): 2 x 2 ablation on fixed model codes, training data.

Factor 1, credited codes: rubric only (VA, VT, MAT, SIZE, RT, DRY, container) vs rubric + discovered
(adds surroundings and COVER; COVER comes from anchor 2a, not the rubric text). Uncredited codes stay off.
Factor 2, threshold: present only vs present or borderline.
  A rubric, present only    B rubric, present or borderline
  C +disc., present only    D +disc., present or borderline (= best guess)
Reported on the remainder (nothing fitted there) and all train, with and without `unfinished`; paired QWK
differences for each factor and the interaction (D - C) - (B - A).

Usage: python set1/eda/step10_ablation.py [extra jsonl runs for a different split, e.g. test]
"""
import json
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, '.')
sys.path.insert(0, 'set1/eda')
from common.evaluate import qwk, report
from step7_cv import BEST, GROUPS, scores

sys.stdout.reconfigure(encoding='utf-8')
RUBRIC = ['VA', 'VT', 'MAT', 'SIZE', 'RT', 'DRY', 'container']
DISCOVERED = ['surroundings', 'COVER']


def cfg(disc, borderline):
    c = {g: 'off' for g in GROUPS}
    for g in RUBRIC + (DISCOVERED if disc else []):
        c[g] = 'borderline' if borderline else 'present'
    return {**c, 'pooled_borderline': 'per-code', 'surroundings_count': 'once', 'container_count': 'once'}


CELLS = {'A rubric, present only': cfg(False, False), 'B rubric, present or borderline': cfg(False, True),
         'C +discovered, present only': cfg(True, False), 'D +discovered, present or borderline': cfg(True, True)}
assert CELLS['D +discovered, present or borderline'] == BEST


def boot(y, cols, f, n=2000, seed=0):
    """Point estimate and percentile 95% CI of f(QWKs of cols) over bootstrap resamples of responses."""
    rng = np.random.default_rng(seed)
    point = f(*[qwk(y, c) for c in cols])
    vals = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        vals.append(f(*[qwk(y[i], c[i]) for c in cols]))
    return point, np.percentile(vals, 2.5), np.percentile(vals, 97.5)


runs = ['set1/results/dev_v0.2.jsonl', 'set1/results/remainder_v0.2.jsonl']
m = pd.DataFrame([json.loads(l) for p in runs for l in open(p, encoding='utf-8')]).drop(columns='split')
m = m.merge(pd.concat([pd.read_csv(f'data/set1/{s}.csv').assign(split=s) for s in ('dev', 'remainder')]),
            on='Id').reset_index(drop=True)
L = {c: m[c].astype(int).to_numpy() for codes in GROUPS.values() for c in codes}
S = {k: scores(L, v) for k, v in CELLS.items()}
unf = m['flags'].map(lambda f: 'unfinished' in f).to_numpy()
y = m.Score1.to_numpy()

for name, keep in (('remainder', (m.split == 'remainder').to_numpy()), ('remainder, without unfinished', (m.split == 'remainder').to_numpy() & ~unf),
                   ('all train', np.ones(len(m), bool)), ('all train, without unfinished', ~unf)):
    print(f'\n== {name} (n={int(keep.sum())}) ==')
    print(pd.DataFrame([report(y[keep], s[keep], k) for k, s in S.items()]).to_string(index=False))
    a, b, c, d = (S[k][keep] for k in CELLS)
    yk = y[keep]
    for label, cols, f in (('discovered codes, present only   (C - A)', [c, a], lambda q1, q2: q1 - q2),
                           ('discovered codes, with borderline (D - B)', [d, b], lambda q1, q2: q1 - q2),
                           ('borderline, rubric only          (B - A)', [b, a], lambda q1, q2: q1 - q2),
                           ('borderline, with discovered      (D - C)', [d, c], lambda q1, q2: q1 - q2),
                           ('interaction (D - C) - (B - A)', [a, b, c, d], lambda qa, qb, qc, qd: (qd - qc) - (qb - qa))):
        p, lo, hi = boot(yk, cols, f)
        print(f'  {label}: {p:+.4f} [{lo:+.4f}, {hi:+.4f}]')
