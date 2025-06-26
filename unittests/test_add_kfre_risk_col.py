import pandas as pd
from kfre import add_kfre_risk_col


def sample_for_risk():
    # minimal 4-var model inputs
    return pd.DataFrame(
        {
            "Age": [50],
            "SEX": ["Male"],
            "eGFR-EPI": [60],
            "uACR": [30],
            "Diabetes (1=yes; 0=no)": [0],
            "Hypertension (1=yes; 0=no)": [0],
            # for 4-var, albumin-/phosphorous-/bicarb-/calcium not used
            "Albumin_g_dl": [4.0],
            "Phosphate_mg_dl": [1.0],
            "Bicarbonate (mmol/L)": [24.0],
            "Calcium_mg_dl": [9.0],
        }
    )


def test_add_kfre_risk_col_4var_2year():
    df = sample_for_risk()
    out = add_kfre_risk_col(
        df.copy(),
        age_col="Age",
        sex_col="SEX",
        eGFR_col="eGFR-EPI",
        uACR_col="uACR",
        dm_col="Diabetes (1=yes; 0=no)",
        htn_col="Hypertension (1=yes; 0=no)",
        albumin_col="Albumin_g_dl",
        phosphorous_col="Phosphate_mg_dl",
        bicarbonate_col="Bicarbonate (mmol/L)",
        calcium_col="Calcium_mg_dl",
        num_vars=[4],
        years=[2],
        is_north_american=True,
        copy=True,
    )
    # column name format: kfre_4_var_2_year
    assert "kfre_4_var_2_year" in out.columns
    val = out["kfre_4_var_2_year"].iloc[0]
    assert isinstance(val, float)
    assert 0 <= val <= 1
