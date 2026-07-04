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
    # should get a "uPCR_mg_g" column
    assert "uPCR_mg_g" in out.columns


def test_perform_conversions_round_trip():
    df = sample_df()
    c = perform_conversions(df.copy(), reverse=False, convert_all=True)
    back = perform_conversions(c.copy(), reverse=True, convert_all=True)
    # original and round-tripped match
    assert back["uPCR"].tolist() == df["uPCR"].tolist()


def test_perform_conversions_roundtrip():
    import pandas as pd
    from kfre import perform_conversions

    df = pd.DataFrame(
        {
            "Calcium (mmol/L)": [2.4],
            "Phosphate (mmol/L)": [1.2],
            "Albumin (g/l)": [40.0],
        }
    )
    fwd = perform_conversions(df, reverse=False, convert_all=True)
    # SI -> conventional lands in sensible clinical ranges
    assert 8.0 <= fwd["Calcium_mg_dl"].iloc[0] <= 11.0
    assert 3.0 <= fwd["Albumin_g_dl"].iloc[0] <= 5.0
    # Round-trip by naming the converted columns explicitly (the supported way;
    # convert_all cannot disambiguate an original column from its own output).
    back = perform_conversions(
        fwd,
        reverse=True,
        calcium_col="Calcium_mg_dl",
        phosphate_col="Phosphate_mg_dl",
        albumin_col="Albumin_g_dl",
    )
    assert abs(back["Calcium_mmol_L"].iloc[0] - 2.4) < 1e-9
    assert abs(back["Albumin_g_L"].iloc[0] - 40.0) < 1e-9
    assert abs(back["Phosphate_mmol_L"].iloc[0] - 1.2) < 1e-9


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
    # column should exist and be numeric
    assert "uACR" in df.columns
    assert isinstance(df["uACR"].iloc[0], float)
    assert df["uACR"].iloc[0] > 0
