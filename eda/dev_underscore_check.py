"""Dev run 1: where does the LLM score below Score1, and does U (misunderstanding) drive it?"""
import sys

import pandas as pd

sys.path.insert(0, '.')
from evaluate import load_run

CODES = ['E', 'J', 'D', 'N', 'P', 'L', 'U']
r = load_run('results/dev_v1.1_r1.jsonl').merge(pd.read_csv('data/set10/dev.csv'), on='Id')
h = pd.read_csv('eda/dev_codes.csv').set_index('Id')
low = r[r.score < r.Score1]
print('LLM below Score1, by (Score1 -> LLM) and whether LLM set U=1:')
print(pd.crosstab([low.Score1, low.score], low.U))
print(f'\nAll LLM U=1: {r.U.sum()} | of those, Score1>0: {(r.U.astype(bool) & (r.Score1 > 0)).sum()} | hand U=1 on same Ids: {h.loc[r.Id[r.U == 1], "U"].sum()}')
pd.set_option('display.max_colwidth', 200)
print('\nScore1=2 scored 0 by LLM:')
x = low[(low.Score1 == 2) & (low.score == 0)]
for row in x.itertuples():
    print(f'\n{row.Id} S1/S2={row.Score1}/{row.Score2} | LLM {"".join(f"{c}{getattr(row, c)}" for c in CODES)} | hand {"".join(f"{c}{h.at[row.Id, c]}" for c in CODES)}')
    print(f'  text: {row.text[:260]}')
    print(f'  LLM: {row.rationale}')
