"""Step 1: Set 1 score distribution, Score1 vs Score2 agreement, word length by score, "^p" responses.

Aggregates over all 1,672 train responses (no text is read), as in Set 10 step 1; the test set is not used.
Word counts are whitespace tokens with "^p" paragraph marks removed.
"""
import sys

import pandas as pd

sys.path.insert(0, '.')
from common.evaluate import report

sys.stdout.reconfigure(encoding='utf-8')
dev = pd.read_csv('data/set1/dev.csv').assign(split='dev')
rem = pd.read_csv('data/set1/remainder.csv').assign(split='remainder')
d = pd.concat([dev, rem], ignore_index=True)
d['words'] = d.text.str.replace('^p', ' ', regex=False).str.split().str.len()
d['has_p'] = d.text.str.contains('^p', regex=False)


def pct(s):
    return s.value_counts(normalize=True).sort_index().mul(100).round(1)


print(f'== 1. Score distribution (train n={len(d)}) ==')
dist = pd.DataFrame({'Score1 n': d.Score1.value_counts().sort_index(), 'Score1 %': pct(d.Score1),
                     'Score2 n': d.Score2.value_counts().sort_index(), 'Score2 %': pct(d.Score2),
                     'dev Score1 %': pct(dev.Score1), 'remainder Score1 %': pct(rem.Score1)})
print(dist.to_string())
print(f'mean Score1 {d.Score1.mean():.3f}, Score2 {d.Score2.mean():.3f}')

print('\n== 2. Score1 (rows) vs Score2 (columns) ==')
print(pd.crosstab(d.Score1, d.Score2, margins=True, margins_name='total').to_string())
print('\nRow % (of each Score1 level):')
print((pd.crosstab(d.Score1, d.Score2, normalize='index') * 100).round(1).to_string())
gap = (d.Score1 - d.Score2)
print(f'\n|Score1 - Score2|: {gap.abs().value_counts().sort_index().to_dict()} | Score2 higher {int((gap < 0).sum())}, lower {int((gap > 0).sum())}')
print('\nScore2 scored against Score1 (as a machine would be):')
print(pd.DataFrame([report(d.Score1, d.Score2, 'Score2 vs Score1')]).to_string(index=False))

print('\n== 3. Words by Score1 level ==')
desc = d.groupby('Score1').words.describe().round(1)
print(desc.to_string())
print(f'Spearman rho(words, Score1) = {d.words.corr(d.Score1, method="spearman"):.3f}')

print(f'\n== 4. Score1 for responses with and without "^p" ==')
ct = pd.crosstab(d.has_p.map({True: 'with ^p', False: 'without ^p'}), d.Score1)
print(ct.assign(n=ct.sum(axis=1)).to_string())
print((pd.crosstab(d.has_p.map({True: 'with ^p', False: 'without ^p'}), d.Score1, normalize='index') * 100).round(1).to_string())
print(f'mean words: with ^p {d[d.has_p].words.mean():.1f}, without {d[~d.has_p].words.mean():.1f} | "^p" responses in dev: {int(dev.text.str.contains("^p", regex=False).sum())}')
