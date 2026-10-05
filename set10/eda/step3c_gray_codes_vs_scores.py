"""Join blind gray codes (D, N, J, L) to scores. Consensus (S1 == S2) first, then splits."""
import pandas as pd

dev = pd.read_csv('data/set10/dev.csv')
dev = dev[dev.text.str.split('::').str[0].str.contains('gray')]
codes = pd.read_csv('set10/eda/gray_codes.csv').fillna('')
assert set(codes.Id) == set(dev.Id) and codes.Id.is_unique, 'codes must cover every gray dev response once'
d = dev.merge(codes, on='Id')
d['misread'] = d.note.str.contains('trial consistency').astype(int)
d['offtarget'] = d.note.str.contains('off-target').astype(int)
d['pattern'] = d.apply(lambda r: f"N{r.N} D{r.D}" + (" J-only" if r.J and not r.N and not r.D else ""), axis=1)
print(f'{len(d)} gray responses | agreed {(d.Score1 == d.Score2).sum()} | split {(d.Score1 != d.Score2).sum()}')

agree = d[d.Score1 == d.Score2]
print('\n1. CONSENSUS (S1 == S2): score counts by code pattern')
print(pd.crosstab(agree.pattern, agree.Score1, margins=True))
print('\n1b. Consensus, N=1 only: score by L (literal reading) and by misread (trial consistency)')
n1 = agree[agree.N == 1]
print(pd.crosstab([n1.D, n1.L, n1.misread], n1.Score1).rename_axis(['D', 'L', 'misread']))
print('\n1c. Consensus, N=0 & D=0: score by J (and off-target)')
nd0 = agree[(agree.N == 0) & (agree.D == 0)]
print(pd.crosstab([nd0.J, nd0.offtarget], nd0.Score1).rename_axis(['J', 'offtarget']))

print('\n2. SPLITS (S1 != S2), with codes')
cols = ['Id', 'Score1', 'Score2', 'D', 'N', 'J', 'L', 'note']
print(d[d.Score1 != d.Score2].sort_values(['N', 'D', 'Score1'])[cols].to_string(index=False))
