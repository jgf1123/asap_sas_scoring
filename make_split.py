"""Build dev / remainder / test files for one ASAP-SAS essay set.

dev        300 random train responses (seed 0): prompt iteration
remainder  rest of train: untouched until the prompt-overfitting check
test       official public-leaderboard responses + released labels: final evaluation, run once

Usage: python make_split.py 10
"""
import sys
from pathlib import Path

import pandas as pd

SET = int(sys.argv[1])
N_DEV = 300
out = Path(f'data/set{SET}')
out.mkdir(parents=True, exist_ok=True)

train = pd.read_csv('data/train.tsv', sep='\t').query('EssaySet == @SET')
train = train.rename(columns={'EssayText': 'text'})[['Id', 'Score1', 'Score2', 'text']]
dev = train.sample(N_DEV, random_state=0)
remainder = train.drop(dev.index)

texts = pd.read_csv('data/public_leaderboard_rel_2.tsv', sep='\t').query('EssaySet == @SET')
labels = pd.read_csv('data/public_leaderboard_solution.csv').query('essay_set == @SET')
test = texts.merge(labels[['id', 'essay_score']], left_on='Id', right_on='id', validate='one_to_one')
test = test.rename(columns={'EssayText': 'text', 'essay_score': 'Score1'})[['Id', 'Score1', 'text']]
assert len(test) == len(texts) == len(labels)

for name, x in (('dev', dev), ('remainder', remainder), ('test', test)):
    x.to_csv(out / f'{name}.csv', index=False)
    dist = x.Score1.value_counts(normalize=True).sort_index().mul(100).round(0).astype(int).to_dict()
    print(f'{name:9s} n={len(x):5d}  Score1 % by level: {dist}')
