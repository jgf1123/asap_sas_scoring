"""Deterministic Set 1 score from codebook codes (rubric.md §5). r is a mapping of code -> level.

A code counts when its level is at least min_level: binary codes (v0.1, my dev codes) use min_level=1;
three-level codes (v0.2: 2 present, 1 borderline, 0 absent) use min_level=2 (primary, only present counts)
or min_level=1 (secondary analysis: borderline also counts).

Score = number of distinct credited pieces, at most 3.
  O2  VA, VT, MAT, SIZE, RT, DRY: one piece each
  D1  CS or CT: one piece (both together still one)
  C1/D2  ENVT, ENVL or ENVP: one piece (any combination still one)
  C2  COVER: one piece
  C3/D3  AMT, MATV, MATK, RINSE, MASS, DESIGN and "other": not credited
  O3  flags do not change the score
"""
PIECES = ['VA', 'VT', 'MAT', 'SIZE', 'RT', 'DRY']


def score(r, min_level=1):
    on = lambda k: int(r[k]) >= min_level
    n = sum(on(k) for k in PIECES)
    n += on('CS') or on('CT')
    n += on('ENVT') or on('ENVL') or on('ENVP')
    n += on('COVER')
    return min(n, 3)
