"""Build dev_codes_v1.csv: blind codes (dev_codes.csv) + auditable overrides (dev_overrides.csv).

Overrides were decided AFTER seeing dev scores, so v1 is fitted, not blind. Each row names the response,
column, blind value, new value and reason; the build fails if a blind value does not match.
Override sets so far:
  SIZE split (2026-10-05): SIZE kept for size/shape/surface area/form; new AMT for amount/mass of sample.
    Rule written before a blind re-read of the 66 SIZE responses (scores not consulted during the re-read);
    motivated by step 2 (SIZE credited only +0.40) and step 2b.
"""
import pandas as pd

c = pd.read_csv('set1/eda/dev_codes.csv', dtype={'other': str, 'flags': str, 'note': str}).fillna('').set_index('Id')
o = pd.read_csv('set1/eda/dev_overrides.csv')
for col in set(o.column) - set(c.columns):
    c.insert(c.columns.get_loc('CT') + 1, col, 0)
for r in o.itertuples():
    assert c.at[r.Id, r.column] == r.old, (r.Id, r.column, c.at[r.Id, r.column], r.old)
    c.at[r.Id, r.column] = r.new
c.reset_index().to_csv('set1/eda/dev_codes_v1.csv', index=False)
print(f'{len(o)} overrides applied -> set1/eda/dev_codes_v1.csv | columns: {list(c.columns)}')
