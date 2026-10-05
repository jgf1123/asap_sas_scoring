"""Rows, columns and Set 10 counts for each Kaggle file."""
import pandas as pd

files = {'train.tsv': '\t', 'train_rel_2.tsv': '\t', 'public_leaderboard.tsv': '\t',
         'public_leaderboard_rel_2.tsv': '\t', 'public_leaderboard_solution.csv': ',',
         'private_leaderboard.tsv': '\t', 'test.csv': ',', 'length_benchmark.csv': ','}
for f, sep in files.items():
    x = pd.read_csv(f'data/{f}', sep=sep)
    set_col = 'EssaySet' if 'EssaySet' in x else None
    n10 = (x[set_col] == 10).sum() if set_col else '-'
    print(f'{f:34s} rows={len(x):6d} set10={n10!s:5s} cols={list(x.columns)}')
