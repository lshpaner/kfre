# tests/test_classification_functions.py

import pandas as pd
from kfre import class_esrd_outcome, class_ckd_stages


def test_class_esrd_outcome_create_years_and_prefix_and_override():
    # durations in days
    df = pd.DataFrame({"flag": [1, 1, 0], "dur_days": [365, 200, 800]})
    # True: create_years_col → uses dur_days/365.25
    out = class_esrd_outcome(
        df.copy(),
        col="flag",
        years=1,
        duration_col="dur_days",
        prefix=None,
        create_years_col=True,
    )
    # new years column
    assert "ESRD_duration_years" in out.columns
    # default column name
    assert "1_year_outcome" in out.columns
    # logic: for flag==1 and yrs<=1 → 1; else 0
    assert out["1_year_outcome"].tolist() == [1, 1, 0]

    # False: use provided duration_col directly, custom prefix
    df2 = pd.DataFrame({"e": [1, 0, 1], "d": [2, 3, 1]})
    out2 = class_esrd_outcome(
        df2.copy(),
        col="e",
        years=2,
        duration_col="d",
        prefix="PRE",
        create_years_col=False,
    )
    # no ESRD_duration_years
    assert "ESRD_duration_years" not in out2.columns
    # custom prefix column
    assert "PRE_2_year_outcome" in out2.columns
    # verify logic
    assert out2["PRE_2_year_outcome"].tolist() == [1, 0, 1]


def test_class_ckd_stages_with_both_columns():
    df = pd.DataFrame({"eG": [95, 75, 50, 35, 20, 10]})
    out = class_ckd_stages(
        df.copy(), egfr_col="eG", stage_col="stage", combined_stage_col="combined"
    )
    # exact stage names
    assert out["stage"].tolist() == [
        "CKD Stage 1",
        "CKD Stage 2",
        "CKD Stage 3a",
        "CKD Stage 3b",
        "CKD Stage 4",
        "CKD Stage 5",
    ]
    # combined only for egfr<60
    assert out["combined"].tolist() == [
        "Not Classified",
        "Not Classified",
        "CKD Stage 3 - 5",
        "CKD Stage 3 - 5",
        "CKD Stage 3 - 5",
        "CKD Stage 3 - 5",
    ]


def test_class_ckd_stages_only_stage_col():
    df = pd.DataFrame({"eG": [10]})
    out = class_ckd_stages(
        df.copy(), egfr_col="eG", stage_col="stg", combined_stage_col=None
    )
    assert out["stg"].iloc[0] == "CKD Stage 5"
    assert "combined" not in out.columns
