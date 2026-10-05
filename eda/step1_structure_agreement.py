import pandas as pd
from sklearn.metrics import cohen_kappa_score

d = pd.read_csv('data/train.tsv', sep='\t')
s = d[d.EssaySet == 10]
print('Columns:', list(d.columns))
print('All sets:', len(d), 'rows; Set 10:', len(s), 'rows')
print('Missing values in Set 10:', s.isna().sum().to_dict())
print('Duplicate ids:', s.Id.duplicated().sum(), '| duplicate texts:', s.EssayText.duplicated().sum())
print('\nOne row, as stored:')
print(s.iloc[0].to_dict())

print('\nScore1 (rows) vs Score2 (columns), counts:')
print(pd.crosstab(s.Score1, s.Score2))
print('\nSame table as % of each Score1 row:')
print((pd.crosstab(s.Score1, s.Score2, normalize='index') * 100).round(0))
print('\nExact agreement: %.3f' % (s.Score1 == s.Score2).mean())
print('Differ by 1 point: %.3f | differ by 2 points: %.3f' % ((s.Score1 - s.Score2).abs().eq(1).mean(), (s.Score1 - s.Score2).abs().eq(2).mean()))
print('Human-vs-human QWK: %.3f' % cohen_kappa_score(s.Score1, s.Score2, weights='quadratic'))
print('Human-vs-human plain kappa: %.3f' % cohen_kappa_score(s.Score1, s.Score2))
