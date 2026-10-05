"""Join blind white/black codes (E, D, N, J, L) to scores. Consensus (S1 == S2) first, then splits."""
import pandas as pd

dev = pd.read_csv('data/set10/dev.csv')
dev = dev[~dev.text.str.split('::').str[0].str.contains('gray')]
codes = pd.read_csv('set10/eda/extreme_codes.csv').fillna('')
assert set(codes.Id) == set(dev.Id) and codes.Id.is_unique, 'codes must cover every white/black dev response once'
d = dev.merge(codes, on='Id')
d['offtarget'] = d.note.str.contains('off-target').astype(int)
d['pattern'] = 'E' + d.E.astype(str) + ' N' + d.N.astype(str) + ' D' + d.D.astype(str)
print(f'{len(d)} white/black responses | agreed {(d.Score1 == d.Score2).sum()} | split {(d.Score1 != d.Score2).sum()}')

agree = d[d.Score1 == d.Score2]
print('\n1. CONSENSUS (S1 == S2): score counts by E / N / D')
print(pd.crosstab(agree.pattern, agree.Score1, margins=True))
print('\n1b. Consensus, E0 N0 D0: off-target vs not')
x = agree[agree.pattern == 'E0 N0 D0']
print(pd.crosstab(x.offtarget, x.Score1))
print('\n1c. Consensus exceptions to "E+N -> 2, exactly one -> 1, neither -> 0":')
expected = (agree.E + agree.N).clip(upper=2)
cols = ['Id', 'Score1', 'E', 'D', 'N', 'J', 'L', 'note']
print(agree.assign(expected=expected).query('expected != Score1')[cols + ['expected']].to_string(index=False))

print('\n2. SPLITS (S1 != S2), with codes and the E+N count')
s = d[d.Score1 != d.Score2].assign(EN=lambda x: x.E + x.N)
print(s.sort_values(['EN', 'Score1'])[['Id', 'Score1', 'Score2', 'EN'] + cols[2:]].to_string(index=False))
print('\nSplits: which rater equals E+N?')
print(pd.Series(['S1' if r.Score1 == r.EN else 'S2' if r.Score2 == r.EN else 'neither' for r in s.itertuples()]).value_counts().to_dict())

print('\n3. Consensus, effect only (E1 N0): score by color chosen')
d['color'] = d.text.str.split('::').str[0].str.strip().str.lower()
agree = d[d.Score1 == d.Score2]
eo = agree[(agree.E == 1) & (agree.N == 0)]
print(pd.crosstab(eo.color, eo.Score1))
print('\n4. Rule "N and D -> 2; else E or J -> 1; else 0" vs consensus and splits')
rule = lambda x: ((x.N == 1) & (x.D == 1)).map({True: 2, False: 0}).where(lambda r: r == 2, ((x.E == 1) | (x.J == 1)).astype(int))
agree = agree.assign(rule=rule(agree))
print('  consensus exact match: %.3f' % (agree.rule == agree.Score1).mean())
s = d[d.Score1 != d.Score2].assign(rule=lambda x: rule(x))
print('  splits matched by:', pd.Series(['S1' if r.Score1 == r.rule else 'S2' if r.Score2 == r.rule else 'neither' for r in s.itertuples()]).value_counts().to_dict())
