"""Print dev responses that have a given blind code: Id and text only, NO scores. "^p" shown as " ⏎ ".

Usage: python set1/eda/dump_blind_code.py SIZE
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
code = sys.argv[1]
c = pd.read_csv('set1/eda/dev_codes.csv', usecols=['Id', code])
dev = pd.read_csv('data/set1/dev.csv', usecols=['Id', 'text'])
x = dev[dev.Id.isin(c.Id[c[code] == 1])].sort_values('Id')
print(f'{len(x)} dev responses coded {code}')
for r in x.itertuples():
    print(f'{r.Id}: {r.text.replace("^p", " ⏎ ")}')
