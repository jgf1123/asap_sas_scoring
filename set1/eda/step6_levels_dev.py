"""Step 6: three-level codes on dev, the analyses pre-registered in set1/eda/prereg_levels.md.

Usage: python set1/eda/step6_levels_dev.py set1/results/dev_v0.2.jsonl [set1/results/<repeat run>.jsonl]
  P1 usage: borderline (level 1) share of code cells; prediction 1-5%.
  P2 validity: share of responses with a borderline code, rater disagreement vs agreement; prediction >= 2x.
  P3 consistency (optional second run): borderline cells that recur at level 1.
  Descriptive: reasons a-f, (f) texts, borderline-entry mismatches, agreement with my binary codes,
  strict (present only) and lenient (borderline also) scores against Score1.
"""
import json
import sys
from collections import Counter

import pandas as pd

sys.path.insert(0, '.')
from common.evaluate import report
from set1.config import CODES
from set1.score_from_codes import score

sys.stdout.reconfigure(encoding='utf-8')


def load(path):
    recs = [json.loads(l) for l in open(path, encoding='utf-8')]
    ok = pd.DataFrame([r for r in recs if 'error' not in r]).drop_duplicates('Id', keep='last').set_index('Id')
    return ok, sum('error' in r for r in recs)


m, n_err = load(sys.argv[1])
dev = pd.read_csv('data/set1/dev.csv').set_index('Id')
m = m.join(dev[['Score1', 'Score2']], how='inner')
L = m[CODES].astype(int)
print(f'{len(m)} responses coded | error records in file: {n_err} | missing: {len(dev) - len(m)}')

cells = L.size
bl = (L == 1)
print(f'\n== P1 usage: borderline cells {int(bl.values.sum())} of {cells} = {bl.values.mean():.2%}'
      f' (prediction 1-5%) | present {(L == 2).values.mean():.2%}, absent {(L == 0).values.mean():.2%}')
print('borderline cells by code:', {c: int(bl[c].sum()) for c in CODES if bl[c].sum()})

m['has_bl'] = bl.any(axis=1)
dis, agr = m[m.Score1 != m.Score2], m[m.Score1 == m.Score2]
r_dis, r_agr = dis.has_bl.mean(), agr.has_bl.mean()
ratio = r_dis / r_agr if r_agr else float('inf')
print(f'\n== P2 validity: responses with a borderline code: rater disagreement {int(dis.has_bl.sum())}/{len(dis)} = {r_dis:.1%},'
      f' agreement {int(agr.has_bl.sum())}/{len(agr)} = {r_agr:.1%}, ratio {ratio:.2f} (prediction >= 2)')

entries = [(i, e['code'], e['reason'], e['note']) for i, es in m['borderline'].items() for e in es]
reasons = Counter(r for _, _, r, _ in entries)
print(f'\n== Reasons: {dict(sorted(reasons.items()))}')
for i, c, r, note in entries:
    if r == 'f':
        print(f'  (f) {i} {c}: {note}')
listed = {(i, c) for i, c, _, _ in entries}
level1 = {(i, c) for i in m.index for c in CODES if L.at[i, c] == 1}
print(f'mismatches: level 1 without entry {len(level1 - listed)}, entry without level 1 {len(listed - level1)}')

mine = pd.read_csv('set1/eda/dev_codes_v01.csv').set_index('Id').loc[m.index]
present = (L == 2).astype(int)
print('\n== Agreement with my binary codes (model present vs mine), cells where model is not borderline ==')
rows = []
for c in CODES:
    nb = L[c] != 1
    rows.append({'code': c, 'both': int(((present[c] == 1) & (mine[c] == 1) & nb).sum()),
                 'model only': int(((present[c] == 1) & (mine[c] == 0) & nb).sum()),
                 'mine only': int(((present[c] == 0) & (mine[c] == 1) & nb).sum()),
                 'model borderline, mine 1': int(((L[c] == 1) & (mine[c] == 1)).sum()),
                 'model borderline, mine 0': int(((L[c] == 1) & (mine[c] == 0)).sum())})
t = pd.DataFrame(rows)
print(t[t.drop(columns='code').sum(axis=1) > 0].to_string(index=False))

recs = m[CODES].to_dict('records')
m['strict'] = [score(r, min_level=2) for r in recs]
m['lenient'] = [score(r, min_level=1) for r in recs]
m['mine'] = [score(r) for r in mine[CODES].to_dict('records')]
unf = m['flags'].map(lambda f: 'unfinished' in f)
print('\n== Scores against Score1 (descriptive; dev is not a held-out test) ==')
for name, x in (('all dev', m), ('excluding model-flagged unfinished', m[~unf])):
    print(f'-- {name} (n={len(x)})')
    print(pd.DataFrame([report(x.Score1, x.Score2, 'Score2 (human)'),
                        report(x.Score1, x.mine, 'my v0.1 codes (fitted)'),
                        report(x.Score1, x.strict, 'model v0.2, present only'),
                        report(x.Score1, x.lenient, 'model v0.2, borderline also')]).to_string(index=False))
dep = m.strict != m.lenient
print(f'responses whose score depends on a borderline code: {int(dep.sum())} ({dep.mean():.1%});'
      f' of these, rater disagreement {int((dep & (m.Score1 != m.Score2)).sum())}')

if len(sys.argv) > 2:
    rep, _ = load(sys.argv[2])
    ids = rep.index.intersection(m.index)
    L2 = rep.loc[ids, CODES].astype(int)
    b1, b2 = (L.loc[ids] == 1), (L2 == 1)
    print(f'\n== P3 consistency on {len(ids)} repeated responses: borderline cells run 1 {int(b1.values.sum())},'
          f' run 2 {int(b2.values.sum())}, both {int((b1 & b2).values.sum())} | cells with identical level'
          f' {(L.loc[ids] == L2).values.mean():.1%}')
