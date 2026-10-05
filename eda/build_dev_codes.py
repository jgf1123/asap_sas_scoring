"""Build eda/dev_codes.csv: sharpened codes for all 300 Set 10 dev responses.

Starts from the blind first-pass codes (gray_codes.csv, extreme_codes.csv) and applies the
sharpened definitions as explicit, auditable overrides. The overrides were made AFTER seeing
scores, so they are fitted, not blind.

Codes
  E  directional temperature effect on the doghouse interior or the dog inside it
     (warmer/cooler, or one-sided "won't get too hot")
  J  two-sided 'just right' claim in temperature terms
  D  directional temperature comparison between colors (incl. superlatives, trends)
  N  experiment result about temperature cited
  P  the experiment result places the CHOSEN color relative to another lid
  L  jar temperature read as the doghouse's temperature
  U  misunderstanding: off-target, misapplied mechanism, wrong direction, contradiction, nonsense
Flags: consistency, hyp, vague, mismatch, physics
"""
import pandas as pd

gray = pd.read_csv('eda/gray_codes.csv').assign(group='gray', E=0)
ext = pd.read_csv('eda/extreme_codes.csv').assign(group='white/black')
d = pd.concat([gray, ext]).fillna({'note': ''}).set_index('Id')
d[['P', 'U']] = 0
d['flags'] = ''

def setv(col, ids, v):
    missing = set(ids) - set(d.index)
    assert not missing, missing
    d.loc[list(ids), col] = v

def flag(name, ids):
    for i in ids:
        d.loc[i, 'flags'] = ';'.join(filter(None, [d.loc[i, 'flags'], name]))

# --- E for gray (not coded in the first pass) ---
setv('E', [25967, 26001, 26025, 26056, 26141, 26151, 26166, 26176, 26189, 26202, 26248, 26328,
           26381, 26385, 26424, 26455, 26478, 26513, 26523, 26536, 26558, 26653, 26662, 26677,
           26734, 26766, 26769, 26780, 26789, 26929, 26933, 26949, 26994, 27005, 27010, 27025,
           27030, 27032, 27040, 27143, 27179, 27254, 27366, 27403, 27439, 27452, 27455, 27508,
           27554, 27575, 27583, 27585], 1)

# --- E must state a direction for the doghouse interior / dog inside ---
setv('E', [26015,   # effect with no direction
           26912,   # effect on the dog outside the doghouse
           27444,   # panting symptoms, no temperature effect stated
           27219],  # energy, not temperature
     0)

# --- J requires temperature terms and two sides ---
setv('J', [27097, 26974, 26828, 26931, 26954, 26964, 27175, 26101,   # comfort only, no temperature terms
           26202, 27143],                                             # one-sided (now E)
     0)

# --- D and N must be about temperature/heat ---
setv('D', [26131, 26546], 0)   # no temperature quantity named
setv('N', [26131], 0)

# --- P: result places the chosen color relative to another lid (N=1 rows only) ---
p_gray = [26025, 26248, 26363, 26478, 26536, 26558, 26653, 26734, 26766, 26845, 26849, 26929,
          27179, 27366, 27416, 27427, 27439, 27583]
p0_ext = [25953, 25980, 26002, 26097, 26310, 26357, 26407, 26476, 26642, 26975, 27037, 27263]
setv('P', p_gray, 1)
ext_n1 = d[(d.group == 'white/black') & (d.N == 1)].index
setv('P', [i for i in ext_n1 if i not in p0_ext], 1)

# --- U: misunderstanding (merges off-target X and misapplied mechanism M) ---
offtarget = d.index[d.note.str.contains('off-target')].tolist()
setv('U', offtarget + [27492,                 # darkness, not temperature
                       26090,                 # warmth at night
                       27501,                 # color as insulation
                       27468,                 # white keeps the dog warm (wrong direction)
                       27037,                 # 80-degree extrapolation
                       26141, 26933],         # self-contradictory
     1)

# --- flags ---
flag('consistency', [26172, 26455, 26527, 26558, 26595, 26769, 27032, 27113, 27215, 27439, 27505, 26357])
flag('hyp', [26302, 26430, 26525, 26993])
flag('vague', [26001, 26478, 26766, 27040, 27509, 26131, 26476, 27263, 27145, 27483, 25980])
flag('mismatch', [26302, 26357, 26642, 26993])
flag('physics', [26140, 26219, 26514, 26762, 26763, 27046, 27142, 27202, 27248, 27408, 26923,
                 26787, 27063, 25954, 26733, 27151, 27222])

assert ((d.P == 0) | (d.N == 1)).all(), 'P requires N'
cols = ['group', 'E', 'J', 'D', 'N', 'P', 'L', 'U', 'flags', 'note']
d[cols].sort_index().to_csv('eda/dev_codes.csv')
print(d[cols].groupby('group')[['E', 'J', 'D', 'N', 'P', 'L', 'U']].sum())
print('rows:', len(d))
