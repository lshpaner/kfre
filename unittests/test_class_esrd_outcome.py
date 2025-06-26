import pandas as pd
from kfre import class_esrd_outcome


def test_class_esrd_outcome_column_created():
    # tiny toy dataset
    df = pd.DataFrame(
        {
            "ESRD": [0, 1, 0],
            "Follow-up YEARS": [2.1, 1.0, 3.5],
        }
    )
    out = class_esrd_outcome(
        df.copy(),
        col="ESRD",
        years=2,
        duration_col="Follow-up YEARS",
        prefix=None,
        create_years_col=False,
    )
    assert "2_year_outcome" in out.columns
    # values match ESRD flag when follow-up >= years
    assert out.loc[0, "2_year_outcome"] == 0
    assert out.loc[1, "2_year_outcome"] == 1
