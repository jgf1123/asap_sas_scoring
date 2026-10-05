"""Pre-registered blind sample: 60 remainder responses (seed 1), printed WITHOUT scores."""
import pandas as pd

rem = pd.read_csv('data/set10/remainder.csv').sample(60, random_state=1)
rem[['Id']].to_csv('eda/remainder_sample_ids.csv', index=False)
for r in rem.sort_values('Id').itertuples():
    color, body = r.text.split('::', 1)
    print(f'{r.Id} [{color.strip().lower() or "(blank)"}] {body.strip()}')
