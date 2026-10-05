"""Fit check (dev, by construction optimistic): sharpened code rule vs agreed scores, per boundary config."""
import itertools
import sys

import pandas as pd

sys.path.insert(0, '.')
from score_from_codes import score

dev = pd.read_csv('data/set10/dev.csv')
d = dev.merge(pd.read_csv('eda/dev_codes.csv'), on='Id')
agree, split = d[d.Score1 == d.Score2], d[d.Score1 != d.Score2]
rules = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']

rows = []
for variants in itertools.product('ab', repeat=len(rules)):
    cfg = dict(zip(rules, variants))
    pa = agree.apply(lambda r: score(r, cfg), axis=1)
    ps = split.apply(lambda r: score(r, cfg), axis=1)
    rows.append({**cfg, 'agreed_match': round((pa == agree.Score1).mean(), 3),
                 'splits_S1': int((ps == split.Score1).sum()), 'splits_S2': int((ps == split.Score2).sum())})
res = pd.DataFrame(rows)
print('All .a:', res[(res[rules] == 'a').all(axis=1)].to_dict('records')[0])
print('All .b:', res[(res[rules] == 'b').all(axis=1)].to_dict('records')[0])
print('\nEffect of each toggle (mean agreed_match, a vs b, over all other settings):')
for b in rules:
    print(f'  {b}: a={res[res[b] == "a"].agreed_match.mean():.3f}  b={res[res[b] == "b"].agreed_match.mean():.3f}')
best = res.sort_values('agreed_match', ascending=False).head(3)
print('\nTop 3 configs:'); print(best.to_string(index=False))

cfg = best.iloc[0][rules].to_dict()
agree = agree.assign(pred=agree.apply(lambda r: score(r, cfg), axis=1))
print('\nBest config, agreed match by group:', agree.groupby('group').apply(lambda x: round((x.pred == x.Score1).mean(), 3)).to_dict())
print('Remaining agreed exceptions (pred -> actual):', agree[agree.pred != agree.Score1].groupby(['pred', 'Score1']).size().to_dict())
print(agree[agree.pred != agree.Score1][['Id', 'group', 'Score1', 'pred', 'E', 'J', 'D', 'N', 'P', 'L', 'U', 'flags', 'note']].to_string(index=False))
