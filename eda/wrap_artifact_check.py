"""Line-wrap artifact: do wrap offsets become exact after collapsing (DEG) and HTML entities? (train text only)"""
import html
import re

import pandas as pd

t = pd.concat([pd.read_csv('data/set10/dev.csv'), pd.read_csv('data/set10/remainder.csv')]).text
body = t.str.split('::', n=1).str[1].str.lstrip()
norm = body.str.replace('(DEG)', '°', regex=False).map(html.unescape)

def peaks(s, L=420):
    rate = pd.Series([s[s.str.len() > i].str[i].eq(' ').mean() for i in range(L)])
    return rate.nlargest(7).round(2).sort_index().to_dict()

print('raw body       top space-rate offsets:', peaks(body))
print('(DEG)/entities collapsed:             ', peaks(norm))

# At the first wrap point (offset 45 if confirmed), what surrounds the space?
k = 45
s = norm[norm.str.len() > k + 1]
at = s.str[k]
ctx = pd.DataFrame({'prev': s.str[k - 1], 'at': at, 'next': s.str[k + 1]})
print(f'\nAt offset {k}: char is a space in {at.eq(" ").mean():.2f} of {len(s)} responses')
sp = ctx[ctx['at'] == ' ']
print('  letter on both sides (likely split word):', round((sp.prev.str.isalpha() & sp.next.str.isalpha()).mean(), 2))
print('  double space at the wrap:               ', round(s.str[k - 1:k + 1].eq('  ').mean() + s.str[k:k + 2].eq('  ').mean(), 3))
