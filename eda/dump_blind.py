"""Print dev responses for the given color group WITHOUT scores, for blind hand-coding.

Usage: python eda/dump_blind.py gray|extreme
"""
import sys
import pandas as pd

group = sys.argv[1]
dev = pd.read_csv('data/set10/dev.csv')
parts = dev.text.str.split('::', n=1, expand=True)
dev['color'] = parts[0].str.strip().str.lower()
dev['body'] = parts[1].fillna('').str.strip()
is_gray = dev.color.str.contains('gray')
sel = dev[is_gray] if group == 'gray' else dev[~is_gray]
for r in sel.sort_values('Id').itertuples():
    print(f'{r.Id} [{r.color or "(blank)"}] {r.body}')
