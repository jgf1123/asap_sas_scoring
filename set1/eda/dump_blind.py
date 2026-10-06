"""Print dev responses for blind coding: Id and text only, NO scores. "^p" shown as " ⏎ ".

Usage: python set1/eda/dump_blind.py START END   (rows START..END-1 of dev sorted by Id)
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
start, end = map(int, sys.argv[1:3])
dev = pd.read_csv('data/set1/dev.csv', usecols=['Id', 'text']).sort_values('Id').reset_index(drop=True)
for r in dev.iloc[start:end].itertuples():
    print(f'[{r.Index}] {r.Id}: {r.text.replace("^p", " ⏎ ")}')
