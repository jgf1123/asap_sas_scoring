"""Pre-registered check (set10/eda/prereg_step2.md): frozen rules on 60 blind-coded remainder responses vs dev."""
import sys

import pandas as pd
from sklearn.metrics import cohen_kappa_score

sys.path.insert(0, '.')
from set10.score_from_codes import score

CONFIGS = {'all-a': 'aaaaaa', 'dev-best': 'bababb', 'all-b': 'bbbbbb'}
RULES = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']
qwk = lambda a, b: cohen_kappa_score(a, b, weights='quadratic')

rem = pd.read_csv('data/set10/remainder.csv').merge(pd.read_csv('set10/eda/remainder_blind_codes.csv'), on='Id')
assert len(rem) == 60 and set(rem.Id) == set(pd.read_csv('set10/eda/remainder_sample_ids.csv').Id)
dev = pd.read_csv('data/set10/dev.csv').merge(pd.read_csv('set10/eda/dev_codes.csv'), on='Id')

rows = []
for name, cfg in CONFIGS.items():
    cfg = dict(zip(RULES, cfg))
    for split, d in (('dev (fitted)', dev), ('remainder (blind)', rem)):
        pred = d.apply(lambda r: score(r, cfg), axis=1)
        ag = d.Score1 == d.Score2
        rows.append({'config': name, 'split': split, 'n': len(d),
                     'agreed exact': round((pred[ag] == d.Score1[ag]).mean(), 3),
                     'exact vs S1': round((pred == d.Score1).mean(), 3),
                     'QWK vs S1': round(qwk(d.Score1, pred), 3)})
print(pd.DataFrame(rows).to_string(index=False))
for split, d in (('dev', dev), ('remainder sample', rem)):
    print(f'Reference, Score2 vs Score1 on {split}: exact {(d.Score1 == d.Score2).mean():.3f}, QWK {qwk(d.Score1, d.Score2):.3f}')
print('Remainder sample Score1 %:', rem.Score1.value_counts(normalize=True).sort_index().mul(100).round(0).to_dict())

cfg = dict(zip(RULES, CONFIGS['all-a']))
rem['pred'] = rem.apply(lambda r: score(r, cfg), axis=1)
print('\nRemainder confusion, all-a (rows Score1, cols rule):'); print(pd.crosstab(rem.Score1, rem.pred))
print('\nRemainder disagreements (all-a):')
cols = ['Id', 'group', 'Score1', 'Score2', 'pred', 'E', 'J', 'D', 'N', 'P', 'L', 'U', 'flags', 'note']
print(rem[rem.pred != rem.Score1][cols].sort_values(['Score1', 'pred']).to_string(index=False))
