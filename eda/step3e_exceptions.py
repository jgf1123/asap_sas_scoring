"""Agreed dev responses whose score the current code rule mispredicts. Writes eda/step3e_exceptions.md."""
import pandas as pd

dev = pd.read_csv('data/set10/dev.csv')
dev['color'] = dev.text.str.split('::').str[0].str.strip().str.lower()
dev['body'] = dev.text.str.split('::', n=1).str[1].str.strip()
gray = dev.merge(pd.read_csv('eda/gray_codes.csv'), on='Id').assign(group='gray', E=None)
ext = dev.merge(pd.read_csv('eda/extreme_codes.csv'), on='Id').assign(group='white/black')
d = pd.concat([gray, ext]).fillna({'note': ''})
assert len(d) == len(dev)

effect = d.J.astype(bool) | d.D.astype(bool)
effect[d.group == 'white/black'] = (d.E.astype(float).astype(bool) | d.J.astype(bool))[d.group == 'white/black']
d['predicted'] = 0
d.loc[effect, 'predicted'] = 1
d.loc[(d.N == 1) & (d.D == 1), 'predicted'] = 2

agree = d[d.Score1 == d.Score2]
print('Agreed exact match by group:', agree.groupby('group').apply(lambda x: round((x.predicted == x.Score1).mean(), 3)).to_dict())
exc = agree[agree.predicted != agree.Score1].sort_values(['predicted', 'Score1', 'group'])
print('Exceptions (predicted -> actual):', exc.groupby(['predicted', 'Score1']).size().to_dict())

lines = ['# Agreed-score exceptions to the current code rule (dev)', '',
         'Rule: N&D -> 2; else effect (white/black: E or J; gray: J or D) -> 1; else 0.', '']
for (p, a), g in exc.groupby(['predicted', 'Score1']):
    lines += [f'## Predicted {p}, actual {a} ({len(g)})', '', '| Id | group | E | D | N | J | L | note | response |', '|---|---|---|---|---|---|---|---|---|']
    for r in g.itertuples():
        e = '' if pd.isna(r.E) else int(r.E)
        lines.append(f'| {r.Id} | {r.group} | {e} | {r.D} | {r.N} | {r.J} | {r.L} | {r.note} | **{r.color}** :: {r.body.replace("|", "/")} |')
    lines.append('')
open('eda/step3e_exceptions.md', 'w', encoding='utf-8').write('\n'.join(lines))
