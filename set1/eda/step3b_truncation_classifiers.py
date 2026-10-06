"""Step 3b: how well can text-only classifiers find truncated transcriptions? (dev)

There is no ground truth (no handwritten originals). Two text-only classifiers of "ends mid-sentence":
  rule   step 1c tagger: dangling or fragment ending
  blind  the `unfinished` flag from blind coding
1. Agreement between them, with the disagreements listed (judge by reading).
2. Proxy for "the raters saw more": BOTH raters score above the v1 rules score from the visible codes
   (v1 is fitted on dev, so this is a proxy). The rate among flagged vs unflagged responses estimates
   precision; the unflagged rate bounds hidden truncation (cuts at a sentence end), mixed with coding misses.
"""
import re
import sys
from collections import Counter

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
CANNOT_END = set('''a an the of to in into on onto for with by from at about as than
and or but because so if that which who whose when where while
is are was were be been being am do does did would will should could can may might must shall have has had
i you we they he she it its their your my our his her
need needs know knows how what much many each every also more very use put make
another other some any this these those there'''.split())
ENV = {'temperature', 'light', 'storage conditions'}

train = pd.concat([pd.read_csv(f'data/set1/{s}.csv') for s in ('dev', 'remainder')])
vocab = Counter(w for t in train.text for w in re.findall(r'[a-z]+', t.lower()))  # text only, same as step 1c


def rule_tag(text):
    t = re.sub(r'(\s|\^p)+$', '', text)
    if t[-1:] in set('.!?)"\''):
        return False
    last = (re.findall(r'[A-Za-z]+', t) or [''])[-1].lower()
    return last in CANNOT_END or vocab[last] < 3


v1 = pd.read_csv('set1/eda/dev_codes_v1.csv', dtype={'other': str, 'flags': str, 'note': str}).fillna('')
labels = v1.other.map(lambda s: {o.strip() for o in s.split(';') if o.strip()})
v1['v1'] = (v1[['VA', 'VT', 'MAT', 'SIZE', 'RT', 'DRY']].sum(axis=1) + v1[['CS', 'CT']].max(axis=1)
            + labels.map(lambda s: int(bool(s & ENV))) + labels.map(lambda s: int('cover containers' in s))).clip(upper=3)
d = pd.read_csv('data/set1/dev.csv').merge(v1, on='Id', validate='one_to_one')
d['rule'] = d.text.map(rule_tag)
d['blind'] = d['flags'].str.contains('unfinished')
d['above'] = (d.Score1 > d.v1) & (d.Score2 > d.v1)

print(f'== 1. Agreement (dev n={len(d)}) ==')
print(pd.crosstab(d.rule, d.blind, rownames=['rule tagger'], colnames=['blind unfinished flag']).to_string())
for r in d[d.rule != d.blind].sort_values('Id').to_dict('records'):
    print(f'  {r["Id"]} rule={r["rule"]} blind={r["blind"]} S={r["Score1"]}/{r["Score2"]} v1={r["v1"]}: ...{r["text"][-70:]!r}')

print('\n== 2. Both raters above the visible-code score (proxy for "raters saw more") ==')
for name, m in (('rule flags', d.rule), ('blind flags', d.blind), ('either flags', d.rule | d.blind),
                ('neither flags', ~(d.rule | d.blind)), ('all dev', d.rule | ~d.rule)):
    x = d[m]
    print(f'{name:14s} n={len(x):3d} | both raters above v1: {int(x.above.sum()):2d} ({x.above.mean():.0%})')
print('\nFlagged responses:')
for r in d[d.rule | d.blind].sort_values('Id').to_dict('records'):
    print(f'  {r["Id"]} rule={r["rule"]:d} blind={r["blind"]:d} S={r["Score1"]}/{r["Score2"]} v1={r["v1"]} above={r["above"]:d}'
          f' words={len(r["text"].split())}: ...{r["text"][-60:]!r}')
