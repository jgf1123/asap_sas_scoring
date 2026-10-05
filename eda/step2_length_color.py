"""Step 2: response length and color choice vs. Score1 (all train), and length counter-examples (dev only)."""
import pandas as pd
from scipy.stats import spearmanr

SET = 10
train = pd.read_csv('data/train.tsv', sep='\t').query('EssaySet == @SET')
dev = pd.read_csv(f'data/set{SET}/dev.csv')

def split(df, col):
    parts = df[col].str.split('::', n=1, expand=True)
    df = df.assign(color=parts[0].str.strip().str.lower(), body=parts[1].fillna('').str.strip())
    return df.assign(words=df.body.str.split().str.len())

train, dev = split(train, 'EssayText'), split(dev, 'text')
print('Responses without a "::" color prefix:', train.EssayText.str.contains('::').eq(False).sum())

print('\n(a) Words in the written part, by Score1 (all train):')
print(train.groupby('Score1').words.describe(percentiles=[.25, .5, .75])[['count', 'min', '25%', '50%', '75%', 'max']])
print('Empty written part:', (train.words == 0).sum())
rho = spearmanr(train.words, train.Score1).statistic
print(f'Spearman rank correlation, words vs Score1: {rho:.2f}')

print('\n(b) Color choice (all train): count and Score1 % by level')
ct = pd.crosstab(train.color, train.Score1)
pct = pd.crosstab(train.color, train.Score1, normalize='index').mul(100).round(0).astype(int)
print(pd.concat([ct.sum(axis=1).rename('n'), pct.add_prefix('% score ')], axis=1).sort_values('n', ascending=False))

print('\n(c) Dev counter-examples')
show = lambda r: print(f'  [Id {r.Id} S1={r.Score1} S2={r.Score2} {r.words}w] {r.color} :: {r.body}')
print('Longest responses scored 0:')
dev[dev.Score1 == 0].nlargest(4, 'words').apply(show, axis=1)
print('Shortest responses scored 2:')
dev[dev.Score1 == 2].nsmallest(4, 'words').apply(show, axis=1)
