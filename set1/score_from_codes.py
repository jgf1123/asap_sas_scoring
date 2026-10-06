"""Deterministic Set 1 score from codebook v0.1 codes (rubric.md §5). r is a mapping of code -> 0/1.

Score = number of distinct credited pieces, at most 3.
  O2  VA, VT, MAT, SIZE, RT, DRY: one piece each
  D1  CS or CT: one piece (both together still one)
  C1/D2  ENVT, ENVL or ENVP: one piece (any combination still one)
  C2  COVER: one piece
  C3/D3  AMT, MATV, MATK, RINSE, MASS, DESIGN and "other": not credited
  O3  flags do not change the score
"""
PIECES = ['VA', 'VT', 'MAT', 'SIZE', 'RT', 'DRY']


def score(r):
    n = sum(int(r[k]) for k in PIECES)
    n += int(r['CS'] or r['CT'])
    n += int(r['ENVT'] or r['ENVL'] or r['ENVP'])
    n += int(r['COVER'])
    return min(n, 3)
