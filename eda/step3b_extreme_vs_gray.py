"""Extreme (white/black) vs gray choices: (a) human agreement, all train; (b) mention of extremes vs score, dev only."""
import pandas as pd
from sklearn.metrics import cohen_kappa_score

SET = 10

def prep(df, col):
    parts = df[col].str.split('::', n=1, expand=True)
    df = df.assign(color=parts[0].str.strip().str.lower(), body=parts[1].fillna('').str.strip().str.lower())
    df = df[df.color != '']
    return df.assign(group=df.color.map(lambda c: 'gray' if 'gray' in c else 'extreme'),
                     words=df.body.str.split().str.len())

train = prep(pd.read_csv('data/train.tsv', sep='\t').query('EssaySet == @SET'), 'EssayText')
print('(a) All train: score distribution and human agreement by group')
for g, x in train.groupby('group'):
    dist = x.Score1.value_counts(normalize=True).sort_index().mul(100).round(0).astype(int).to_dict()
    print(f'  {g:8s} n={len(x):4d}  Score1 %={dist}  exact={(x.Score1 == x.Score2).mean():.3f}'
          f'  QWK={cohen_kappa_score(x.Score1, x.Score2, weights="quadratic"):.3f}')
    print('    S1 vs S2 off-diagonal counts:', pd.crosstab(x.Score1, x.Score2).stack().loc[lambda s: s.index.get_level_values(0) != s.index.get_level_values(1)].to_dict())

dev = prep(pd.read_csv(f'data/set{SET}/dev.csv'), 'text')
mentions = lambda b, words: b.str.contains(r'\b(?:' + '|'.join(words) + r')\b', regex=True)
dev['mentions_extreme'] = mentions(dev.body, ['black', 'white'])
opposite = {'white': 'black', 'black': 'white'}
dev['mentions_opposite'] = [bool(pd.Series([b]).str.contains(rf'\b{opposite[c]}\b').iloc[0]) if c in opposite else None
                            for b, c in zip(dev.body, dev.color)]

print('\n(b) Dev: gray responses, mentions "black" or "white" vs Score1')
gray = dev[dev.group == 'gray']
print(pd.crosstab(gray.mentions_extreme, gray.Score1, margins=True))
print('  median words:', gray.groupby('mentions_extreme').words.median().to_dict())
print('  median words by score and mention:'); print(gray.pivot_table(index='mentions_extreme', columns='Score1', values='words', aggfunc='median'))

print('\n(b2) Dev: white/black responses, mentions the opposite extreme vs Score1')
ext = dev[dev.group == 'extreme']
print(pd.crosstab(ext.mentions_opposite, ext.Score1, margins=True))
print('  median words:', ext.groupby('mentions_opposite').words.median().to_dict())
