import io
import sys
import numpy as np
import pandas as pd
import pytest

from kfre.main import (
    RiskPredictor,
    predict_kfre,
    add_kfre_risk_col,
    perform_conversions,
    risk_pred,
    upcr_uacr,
)

# --- Helper sample DataFrames ------------------------


def df_basic():
    # Only the 4-variable inputs
    return pd.DataFrame(
        {
            "Age": [50],
            "SEX": ["Male"],
            "eGFR": [60],
            "uACR": [30],
            "Diabetes (1=yes; 0=no)": [1],
            "Hypertension (1=yes; 0=no)": [0],
            # For 8-var:
            "albumin": [4.0],
            "phosphorous": [1.0],
            "bicarbonate": [24.0],
            "calcium": [9.0],
        }
    )


# --- Tests for RiskPredictor.predict_kfre (4,6,8 var) ----


def test_predict_kfre_4var_basic():
    df = df_basic()[["Age", "SEX", "eGFR", "uACR"]]
    cols = {"age": "Age", "sex": "SEX", "eGFR": "eGFR", "uACR": "uACR"}
    rp = RiskPredictor(df, cols)
    out = rp.predict_kfre(years=2, is_north_american=True, use_extra_vars=False)
    # Should return an array/Series of length 1
    assert hasattr(out, "__len__") and len(out) == 1


def test_predict_kfre_6var_branch():
    df = df_basic()[
        [
            "Age",
            "SEX",
            "eGFR",
            "uACR",
            "Diabetes (1=yes; 0=no)",
            "Hypertension (1=yes; 0=no)",
        ]
    ]
    cols = {
        "age": "Age",
        "sex": "SEX",
        "eGFR": "eGFR",
        "uACR": "uACR",
        "dm": "Diabetes (1=yes; 0=no)",
        "htn": "Hypertension (1=yes; 0=no)",
    }
    rp = RiskPredictor(df, cols)
    out6 = rp.predict_kfre(
        years=5, is_north_american=False, use_extra_vars=True, num_vars=6
    )
    assert len(out6) == 1


def test_predict_kfre_8var_branch():
    df = df_basic()
    cols = {
        "age": "Age",
        "sex": "SEX",
        "eGFR": "eGFR",
        "uACR": "uACR",
        "albumin": "albumin",
        "phosphorous": "phosphorous",
        "bicarbonate": "bicarbonate",
        "calcium": "calcium",
    }
    rp = RiskPredictor(df, cols)
    out8 = rp.predict_kfre(
        years=2, is_north_american=False, use_extra_vars=True, num_vars=8
    )
    assert len(out8) == 1


def test_predict_kfre_invalid_model():
    df = df_basic()[["Age", "SEX", "eGFR", "uACR"]]
    cols = {"age": "Age", "sex": "SEX", "eGFR": "eGFR", "uACR": "uACR"}
    rp = RiskPredictor(df, cols)
    # invalid num_vars with use_extra_vars should simply return None
    result = rp.predict_kfre(
        years=2, is_north_american=True, use_extra_vars=True, num_vars=5
    )
    assert result is None


# --- Tests for RiskPredictor.kfre_person error cases (lines 349-350) ---


def test_kfre_person_raises_all_errors():
    rp = RiskPredictor(df=None, columns=None)
    with pytest.raises(ValueError) as ei:
        rp.kfre_person(
            age=None,
            is_male=None,
            eGFR=None,
            uACR=None,
            is_north_american=None,
            years=3,
            dm=2,
            htn=5,
        )
    msg = str(ei.value)
    # should mention each required-field error
    assert "Must supply a value for age" in msg
    assert "Must specify sex" in msg
    assert "Must supply a value for eGFR" in msg
    assert "Must supply a value for uACR" in msg
    assert "Value must be 2 or 5" in msg
    assert "dm parameter" in msg
    assert "htn parameter" in msg
    assert "Must specify True or False for is_north_american" in msg


# --- Tests for upcr_uacr (lines 441-442) ----------------


def test_upcr_uacr_partial_and_full():
    df = pd.DataFrame(
        {
            "uPCR": [50, 100, 200],
            "SEX": ["Female", "Male", "Female"],
            "Diabetes (1=yes; 0=no)": [1, np.nan, 1],
            "Hypertension (1=yes; 0=no)": [0, 1, np.nan],
        }
    )
    res = upcr_uacr(
        df,
        sex_col="SEX",
        diabetes_col="Diabetes (1=yes; 0=no)",
        hypertension_col="Hypertension (1=yes; 0=no)",
        upcr_col="uPCR",
        female_str="Female",
    )
    # Only index 0 has both masks present
    assert not np.isnan(res.iloc[0])
    assert np.isnan(res.iloc[1])
    assert np.isnan(res.iloc[2])


# --- Tests for wrapper functions (lines 616–653) ---------


def test_predict_kfre_wrapper_vs_class():
    df = df_basic()
    cols = {
        "age": "Age",
        "sex": "SEX",
        "eGFR": "eGFR",
        "uACR": "uACR",
        "dm": "Diabetes (1=yes; 0=no)",
        "htn": "Hypertension (1=yes; 0=no)",
        "albumin": "albumin",
        "phosphorous": "phosphorous",
        "bicarbonate": "bicarbonate",
        "calcium": "calcium",
    }
    # compare wrapper result to direct class method
    w = predict_kfre(
        df, cols, years=2, is_north_american=True, use_extra_vars=True, num_vars=6
    )
    rp = RiskPredictor(df, cols)
    c = rp.predict_kfre(
        years=2, is_north_american=True, use_extra_vars=True, num_vars=6
    )
    # they should be numerically close
    assert np.allclose(w, c)


def test_add_kfre_risk_col_inplace_and_copy():
    df = df_basic()
    # missing some cols -> should error
    with pytest.raises(ValueError):
        add_kfre_risk_col(
            df.copy(), age_col=None, sex_col="SEX", eGFR_col="eGFR", uACR_col="uACR"
        )
    # valid 4-var, 2-year
    df2 = add_kfre_risk_col(
        df_basic(),
        age_col="Age",
        sex_col="SEX",
        eGFR_col="eGFR",
        uACR_col="uACR",
        num_vars=4,
        years=2,
        is_north_american=False,
        copy=False,
    )
    assert "kfre_4var_2year" in df2.columns


# --- Tests for perform_conversions (lines 683, 692) -----


def test_perform_conversions_print_and_suffix():
    data = {"uPCR": [100], "Calcium": [9], "Phosphate": [1], "Albumin": [4]}
    df = pd.DataFrame(data)
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    out = perform_conversions(df, reverse=False, convert_all=True)
    sys.stdout = old
    txt = buf.getvalue()
    assert "Converted 'uPCR'" in txt
    # new columns
    assert "uPCR_mg_g" in out.columns
    assert "Calcium_mg_dl" in out.columns


# --- Tests for risk_pred branches (lines 223 etc) -------


def test_risk_pred_4var_vs_6var_vs_8var_consistency():
    # 4-var
    r4 = risk_pred(50, 1, 60, 30, True, years=2)
    # 6-var
    r6 = risk_pred(50, 1, 60, 30, False, dm=0, htn=1, years=5)
    # 8-var
    r8 = risk_pred(
        50,
        0,
        60,
        30,
        True,
        albumin=4,
        phosphorous=1,
        bicarbonate=24,
        calcium=9,
        years=2,
    )
    for r in (r4, r6, r8):
        assert isinstance(r, float)
        assert 0 <= r <= 1
