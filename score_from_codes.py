"""Deterministic score from rubric codes, with boundary-rule toggles (see rubric.md §4).

r is a mapping with keys group, E, J, D, N, P, L, U, flags. Use r['key'], not r.key:
on a pandas row, r.flags is the Series metadata attribute, not the column.
cfg maps a boundary rule ('B1'..'B6') to its variant 'a' or 'b'.
"""

def has(flags, name):
    return name in str(flags).split(';')


def score(r, cfg):
    flags = r['flags']
    n = bool(r['N'])
    if has(flags, 'hyp') and cfg['B3'] == 'a':
        n = False
    if has(flags, 'vague') and cfg['B4'] == 'a':
        n = False
    p = bool(r['P']) and n
    effect = bool(r['E'] or r['J'])

    if r['group'] == 'gray':
        full = p and effect                      # O4b: gray needs placement + a stated goal
    else:
        full = n and bool(r['E'] or r['D'])      # O4a/C2: white/black may cite an absolute result
    if full:
        return 1 if (has(flags, 'mismatch') and cfg['B5'] == 'b') else 2
    if r['U']:                                   # C1 (v1.2): below full credit, so an incidental misconception keeps a 2
        return 0

    if has(flags, 'consistency') and not p:
        return int(effect) if cfg['B1'] == 'b' else 0
    if r['L'] and n and not p:
        return int(effect) if cfg['B2'] == 'b' else 0
    if effect or n:                              # O2: effect without results, or results without effect
        return 1
    if has(flags, 'physics') or r['D']:
        return 1 if cfg['B6'] == 'b' else 0
    return 0
