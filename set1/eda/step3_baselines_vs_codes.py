"""Step 3: baselines vs codebook scores on dev, and responses where a baseline is closer to Score1.

Scorers (all vs Score1):
  Score2                     human reference
  blind count                min(3, rubric codes from the blind pass)                     -- not tuned
  v1 consensus rules         min(3, VA+VT+MAT+SIZE+RT+DRY + container once + environment once + cover)
                             on v1 codes                                                 -- FITTED on dev
  bag-of-words, length-only  fit on remainder, predict dev (common/baselines.py --set 1 --dev)
Then lists responses where bag-of-words is closer to Score1 than v1 rules (|bow - S1| < |v1 - S1|),
split by whether the raters agree.
"""
import sys

import pandas as pd

sys.path.insert(0, '.')
from common.evaluate import report

sys.stdout.reconfigure(encoding='utf-8')
BLIND = ['VA', 'VT', 'MAT', 'SIZE', 'RT', 'DRY', 'CS', 'CT']
ENV = {'temperature', 'light', 'storage conditions'}
dev = pd.read_csv('data/set1/dev.csv')
b = pd.read_csv('set1/results/baselines_dev_predictions.csv').rename(
    columns={'bag-of-words (raw text)': 'bow', 'length-only': 'length'})
blind = pd.read_csv('set1/eda/dev_codes.csv', usecols=['Id'] + BLIND)
v1 = pd.read_csv('set1/eda/dev_codes_v1.csv', dtype={'other': str, 'flags': str, 'note': str}).fillna('')
labels = v1.other.map(lambda s: {o.strip() for o in s.split(';') if o.strip()})
v1['v1'] = (v1[['VA', 'VT', 'MAT', 'SIZE', 'RT', 'DRY']].sum(axis=1) + v1[['CS', 'CT']].max(axis=1)
            + labels.map(lambda s: int(bool(s & ENV))) + labels.map(lambda s: int('cover containers' in s))).clip(upper=3)
blind['blind'] = blind[BLIND].sum(axis=1).clip(upper=3)
d = dev.merge(b, on='Id').merge(blind[['Id', 'blind']], on='Id').merge(v1, on='Id', validate='one_to_one')

print(f'== Agreement with Score1 (dev n={len(d)}) ==')
rows = [report(d.Score1, d.Score2, 'Score2 (human)'),
        report(d.Score1, d.blind, 'blind code count (not tuned)'),
        report(d.Score1, d.v1, 'v1 consensus rules (fitted on dev)'),
        report(d.Score1, d.bow, 'bag-of-words (fit on remainder)'),
        report(d.Score1, d.length, 'length-only (fit on remainder)')]
print(pd.DataFrame(rows).to_string(index=False))

d['agree'] = d.Score1 == d.Score2
for base in ('bow', 'length'):
    for codes in ('v1', 'blind'):
        closer = (d[base] - d.Score1).abs() < (d[codes] - d.Score1).abs()
        worse = (d[base] - d.Score1).abs() > (d[codes] - d.Score1).abs()
        print(f'{base} vs {codes}: {base} closer on {int(closer.sum())} ({int((closer & d.agree).sum())} with raters agreeing),'
              f' {codes} closer on {int(worse.sum())}, tie {int((~closer & ~worse).sum())}')

CODES = ['VA', 'VT', 'MAT', 'MATV', 'MATK', 'SIZE', 'AMT', 'RT', 'DRY', 'CS', 'CT']
x = d[(d.bow - d.Score1).abs() < (d.v1 - d.Score1).abs()].sort_values(['agree', 'Id'], ascending=[False, True])
print(f'\n== Responses where bag-of-words is closer to Score1 than v1 rules (n={len(x)}) ==')
for r in x.to_dict('records'):
    codes = ','.join(k for k in CODES if r[k]) or '-'
    print(f'{r["Id"]} {"AGREED  " if r["agree"] else "disagree"} S1={r["Score1"]} S2={r["Score2"]} bow={r["bow"]} v1={r["v1"]}'
          f' blind={r["blind"]} | {codes} | other: {r["other"] or "-"} | flags: {r["flags"] or "-"}')
    print(f'    {r["text"].replace("^p", " ⏎ ")}')
