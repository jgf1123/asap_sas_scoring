"""Do spaces occur at fixed character offsets more than chance? (line-wrap artifact check, all Set 10 train)

Offsets are measured from the start of the written part (after '::').
"""
import pandas as pd

t = pd.read_csv('data/train.tsv', sep='\t').query('EssaySet == 10').EssayText
body = t.str.split('::', n=1).str[1].str.lstrip()
L = 400
rate = pd.Series([body[body.str.len() > i].str[i].eq(' ').mean() for i in range(L)])
print('Overall space rate: %.3f' % rate.mean())
peaks = rate[rate > 0.5]
print('Offsets with space rate > 0.5:', peaks.round(2).to_dict())
print('Top 8 offsets by space rate:', rate.nlargest(8).round(2).to_dict())
