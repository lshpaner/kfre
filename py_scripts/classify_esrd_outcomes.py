import os
import pandas as pd

from kfre import class_esrd_outcome
from conversions import data

terminal_size = os.get_terminal_size()

df = pd.DataFrame(data)
print(f"\n{df}")

# 2-year outcome
df = class_esrd_outcome(
    df=df,
    col="ESRD",
    years=2,
    duration_col="Follow-up YEARS",
    prefix=None,
    create_years_col=False,
)

# 5-year outcome
df = class_esrd_outcome(
    df=df,
    col="ESRD",
    years=5,
    duration_col="Follow-up YEARS",
    prefix=None,
    create_years_col=False,
)

print("-" * terminal_size.columns)
print(f"\n{df[[col for col in df.columns if 'year_outcome' in col]]}\n")
