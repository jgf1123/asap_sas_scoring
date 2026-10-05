"""Compare train vs train_rel_2 for Set 10; summarize public-leaderboard labels for Set 10."""
import pandas as pd

a = pd.read_csv('data/train.tsv', sep='\t').query('EssaySet == 10').set_index('Id')
b = pd.read_csv('data/train_rel_2.tsv', sep='\t').query('EssaySet == 10').set_index('Id')
print('Set 10 ids identical:', a.index.equals(b.index))
print('Text changed:', (a.EssayText != b.EssayText).sum(),
      '| Score1 changed:', (a.Score1 != b.Score1).sum(), '| Score2 changed:', (a.Score2 != b.Score2).sum())
diff = a.index[a.EssayText != b.EssayText][:2]
for i in diff:
    print('  old:', a.EssayText[i][:150]); print('  new:', b.EssayText[i][:150])

full = pd.read_csv('data/train.tsv', sep='\t'); rel = pd.read_csv('data/train_rel_2.tsv', sep='\t')
print('Rows dropped in rel_2 by set:', full[~full.Id.isin(rel.Id)].EssaySet.value_counts().sort_index().to_dict())

sol = pd.read_csv('data/public_leaderboard_solution.csv').query('essay_set == 10')
pub = pd.read_csv('data/public_leaderboard_rel_2.tsv', sep='\t').query('EssaySet == 10')
print('\nPublic leaderboard Set 10: texts', len(pub), '| labels', len(sol), '| ids match:', set(pub.Id) == set(sol.id))
print('Usage column:', sol.Usage.value_counts().to_dict())
print('Label % by level:', sol.essay_score.value_counts(normalize=True).sort_index().mul(100).round(0).to_dict())
print('Train Score1 % by level:', a.Score1.value_counts(normalize=True).sort_index().mul(100).round(0).to_dict())
