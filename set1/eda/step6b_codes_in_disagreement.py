"""Step 6b: code usage where the human raters disagree (dev, model v0.2 codes; exploratory).

The model's codes are used because the model never saw scores.
A. Per code: share of responses with the code present (2) and borderline (1), rater disagreement (n=32)
   vs agreement (n=268), with counts.
B. Per disagreement: strict score (present only) and lenient score (borderline also) vs the lower and higher
   rater. "bracketed" = strict equals the lower rater and lenient equals the higher: the borderline code(s)
   are the contested piece.
C. Listing of all disagreements with present codes, borderline codes (reason), other, flags, text.
"""
import json
import sys

import pandas as pd

sys.path.insert(0, '.')
from set1.config import CODES
from set1.score_from_codes import score

sys.stdout.reconfigure(encoding='utf-8')
path = sys.argv[1] if len(sys.argv) > 1 else 'set1/results/dev_v0.2.jsonl'
m = pd.DataFrame([json.loads(l) for l in open(path, encoding='utf-8')]).set_index('Id')
m = m.join(pd.read_csv('data/set1/dev.csv').set_index('Id'))
L = m[CODES].astype(int)
dis = m.Score1 != m.Score2
nd, na = int(dis.sum()), int((~dis).sum())

print(f'== A. Code levels, disagreement (n={nd}) vs agreement (n={na}) ==')
rows = []
for c in CODES:
    pd_, pa = int((L[c][dis] == 2).sum()), int((L[c][~dis] == 2).sum())
    bd, ba = int((L[c][dis] == 1).sum()), int((L[c][~dis] == 1).sum())
    rows.append({'code': c,
                 'present dis': f'{pd_} ({pd_ / nd:.0%})', 'present agr': f'{pa} ({pa / na:.0%})',
                 'present ratio': round((pd_ / nd) / (pa / na), 2) if pa else None,
                 'borderline dis': f'{bd} ({bd / nd:.0%})', 'borderline agr': f'{ba} ({ba / na:.0%})',
                 'borderline ratio': round((bd / nd) / (ba / na), 2) if ba else None})
print(pd.DataFrame(rows).to_string(index=False))

recs = m[CODES].to_dict('records')
m['strict'] = [score(r, min_level=2) for r in recs]
m['lenient'] = [score(r, min_level=1) for r in recs]
x = m[dis].copy()
x['lo'], x['hi'] = x[['Score1', 'Score2']].min(axis=1), x[['Score1', 'Score2']].max(axis=1)


def kind(r):
    if r.strict == r.lenient:
        return 'no borderline effect: ' + ('at lower rater' if r.strict == r.lo else
                                           'at higher rater' if r.strict == r.hi else 'at neither')
    if r.strict == r.lo and r.lenient == r.hi:
        return 'bracketed'
    return f'borderline effect, not bracketed'


x['type'] = x.apply(kind, axis=1)
print(f'\n== B. Disagreements by how the borderline level relates to the two raters (n={len(x)}) ==')
print(x.type.value_counts().to_string())

print('\n== C. All disagreements ==')
for t, g in x.groupby('type'):
    print(f'\n-- {t} (n={len(g)}) --')
    for i, r in g.sort_index().iterrows():
        pres = ','.join(c for c in CODES if L.at[i, c] == 2) or '-'
        bl = ','.join(f'{e["code"]}({e["reason"]})' for e in r['borderline']) or '-'
        print(f'{i} S1={r.Score1} S2={r.Score2} strict={r.strict} lenient={r.lenient} | present: {pres} | borderline: {bl}'
              f' | other: {r["other"] or "-"} | flags: {r["flags"] or "-"}')
        print(f'    {r.text.replace("^p", " / ")}')
        for e in r['borderline']:
            print(f'    [{e["code"]} ({e["reason"]})] {e["note"]}')
