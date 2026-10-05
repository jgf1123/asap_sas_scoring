"""Do public_leaderboard.tsv (release 1) and public_leaderboard_rel_2.tsv agree for Set 10? Which sets differ?"""
import pandas as pd

a = pd.read_csv('data/public_leaderboard.tsv', sep='\t')
b = pd.read_csv('data/public_leaderboard_rel_2.tsv', sep='\t')
print('rows per set, release 1 vs rel_2:')
print(pd.concat([a.EssaySet.value_counts().rename('rel1'), b.EssaySet.value_counts().rename('rel2')], axis=1).sort_index().T)
a10, b10 = a[a.EssaySet == 10].set_index('Id'), b[b.EssaySet == 10].set_index('Id')
print('Set 10: same ids', a10.index.equals(b10.index), '| text differs in', int((a10.EssayText != b10.EssayText).sum()))
