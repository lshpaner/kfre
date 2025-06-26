import pandas as pd
from kfre import perform_conversions, upcr_uacr


def sample_df():
    return pd.DataFrame(
        {
            "uPCR": [100.0],
            "SEX": ["Male"],
            "Diabetes (1=yes; 0=no)": [0],
            "Hypertension (1=yes; 0=no)": [0],
        }
    )


def test_perform_conversions_adds_unit_cols():
    df = sample_df()
    out = perform_conversions(df.copy(), reverse=False, convert_all=True)
    # you should get a "uPCR_mg_g" column
    assert "uPCR_mg_g" in out.columns


def test_perform_conversions_round_trip():
    df = sample_df()
    c = perform_conversions(df.copy(), reverse=False, convert_all=True)
    back = perform_conversions(c.copy(), reverse=True, convert_all=True)
    # original and round-tripped match
    assert back["uPCR"].tolist() == df["uPCR"].tolist()


def test_upcr_uacr_male_passthrough():
    df = perform_conversions(sample_df().copy(), reverse=False, convert_all=True)
    df["uACR"] = upcr_uacr(
        df=df,
        sex_col="SEX",
        diabetes_col="Diabetes (1=yes; 0=no)",
        hypertension_col="Hypertension (1=yes; 0=no)",
        upcr_col="uPCR_mg_g",
        female_str="Female",
    )
    # for a male with no modifiers, uACR == uPCR
    assert df["uACR"].iloc[0] == 100.0
