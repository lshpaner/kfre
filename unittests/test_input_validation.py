"""
Regression tests for the four input-handling defects reported in the SoftwareX
review of kfre (SOFTX-D-26-00673, Reviewer #2). Each test fails on 0.1.17 and
passes on the fixed release.

Bug 1: risk_pred raised UnboundLocalError when 6- and 8-variable inputs were
       supplied together.
Bug 2: RiskPredictor.predict_kfre returned None for an unsupported num_vars
       instead of raising ValueError.
Bug 3: unrecognized/missing sex values were silently coerced to one category
       in the batch paths (upcr_uacr, RiskPredictor.predict_kfre).
Bug 4: non-positive uACR was silently clamped to 1e-6, turning invalid data
       into a valid-looking prediction.

Run with:  pytest unittests/test_input_validation.py
"""

import warnings

import numpy as np
import pandas as pd
import pytest

from kfre import (
    kfre_person,
    predict_kfre,
    add_kfre_risk_col,
    upcr_uacr,
    RiskPredictor,
)
from kfre.main import risk_pred


# ---------------------------------------------------------------------------
# Bug 1 - overlapping 6-/8-variable inputs must not crash
# ---------------------------------------------------------------------------
class TestBug1ModelSelection:
    def test_all_inputs_does_not_crash_and_returns_8var(self):
        # dm/htn AND the four biochemical values supplied together.
        full = risk_pred(
            age=60,
            sex=1,
            eGFR=25,
            uACR=200,
            is_north_american=False,
            dm=1,
            htn=1,
            albumin=3.5,
            phosphorous=4.0,
            bicarbonate=24,
            calcium=9.0,
            years=2,
        )
        only_8 = risk_pred(
            age=60,
            sex=1,
            eGFR=25,
            uACR=200,
            is_north_american=False,
            albumin=3.5,
            phosphorous=4.0,
            bicarbonate=24,
            calcium=9.0,
            years=2,
        )
        # 8 > 6 > 4 precedence: full inputs resolve to the 8-variable model.
        assert np.isfinite(full)
        assert np.isclose(full, only_8)

    def test_kfre_person_all_inputs_does_not_crash(self):
        r = kfre_person(
            age=60,
            is_male=True,
            eGFR=25,
            uACR=200,
            is_north_american=False,
            years=2,
            dm=1,
            htn=1,
            albumin=3.5,
            phosphorous=4.0,
            bicarbonate=24,
            calcium=9.0,
        )
        assert np.isfinite(r)

    def test_explicit_num_vars_override(self):
        kw = dict(
            age=60,
            sex=1,
            eGFR=25,
            uACR=200,
            is_north_american=False,
            dm=1,
            htn=1,
            albumin=3.5,
            phosphorous=4.0,
            bicarbonate=24,
            calcium=9.0,
            years=2,
        )
        r4 = risk_pred(**kw, num_vars=4)
        r6 = risk_pred(**kw, num_vars=6)
        r8 = risk_pred(**kw, num_vars=8)
        assert len({round(float(r4), 6), round(float(r6), 6), round(float(r8), 6)}) == 3

    def test_explicit_num_vars_without_inputs_raises(self):
        with pytest.raises(ValueError):
            risk_pred(
                age=60, sex=1, eGFR=25, uACR=200, is_north_american=False, num_vars=8
            )  # no biochem inputs


# ---------------------------------------------------------------------------
# Bug 2 - unsupported num_vars must raise, not return None
# ---------------------------------------------------------------------------
class TestBug2NumVarsValidation:
    def _predictor(self):
        cols = {
            "age": "Age",
            "sex": "Sex",
            "eGFR": "eGFR",
            "uACR": "uACR",
            "region": "Region",
            "dm": "DM",
            "htn": "HTN",
        }
        df = pd.DataFrame(
            {
                "Age": [60],
                "Sex": ["male"],
                "eGFR": [25],
                "uACR": [200],
                "Region": [0],
                "DM": [1],
                "HTN": [1],
            }
        )
        return RiskPredictor(df=df, columns=cols)

    @pytest.mark.parametrize("bad", [0, 3, 5, 7, 9])
    def test_unsupported_num_vars_raises(self, bad):
        with pytest.raises(ValueError):
            self._predictor().predict_kfre(
                years=2,
                is_north_american=False,
                use_extra_vars=True,
                num_vars=bad,
            )

    def test_convenience_wrapper_also_raises(self):
        cols = {
            "age": "Age",
            "sex": "Sex",
            "eGFR": "eGFR",
            "uACR": "uACR",
            "region": "Region",
            "dm": "DM",
            "htn": "HTN",
        }
        df = pd.DataFrame(
            {
                "Age": [60],
                "Sex": ["male"],
                "eGFR": [25],
                "uACR": [200],
                "Region": [0],
                "DM": [1],
                "HTN": [1],
            }
        )
        with pytest.raises(ValueError):
            predict_kfre(
                df,
                cols,
                years=2,
                is_north_american=False,
                use_extra_vars=True,
                num_vars=5,
            )

    def test_valid_num_vars_return_values(self):
        p = self._predictor()
        for nv, extra in [(4, False), (6, True)]:
            out = p.predict_kfre(
                years=2, is_north_american=False, use_extra_vars=extra, num_vars=nv
            )
            assert out is not None
            assert np.isfinite(float(out.iloc[0]))


# ---------------------------------------------------------------------------
# Bug 3 - unrecognized/missing sex -> NaN (not silently coerced)
# ---------------------------------------------------------------------------
class TestBug3SexHandling:
    def test_upcr_uacr_unrecognized_sex_is_nan(self):
        df = pd.DataFrame(
            {
                "SEX": ["Female", "Femal", "", np.nan, "male"],
                "DM": [0] * 5,
                "HTN": [0] * 5,
                "UPCR": [500] * 5,
            }
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = upcr_uacr(
                df,
                sex_col="SEX",
                diabetes_col="DM",
                hypertension_col="HTN",
                upcr_col="UPCR",
                female_str="Female",
            )
        assert pd.notna(res.iloc[0])  # Female
        assert pd.notna(res.iloc[4])  # male
        assert pd.isna(res.iloc[1])  # 'Femal' typo
        assert pd.isna(res.iloc[2])  # empty
        assert pd.isna(res.iloc[3])  # NaN

    def test_upcr_uacr_warns_on_unrecognized(self):
        df = pd.DataFrame(
            {
                "SEX": ["Female", "Femal", "unknown"],
                "DM": [0, 0, 0],
                "HTN": [0, 0, 0],
                "UPCR": [500, 500, 500],
            }
        )
        with pytest.warns(UserWarning):
            upcr_uacr(
                df,
                sex_col="SEX",
                diabetes_col="DM",
                hypertension_col="HTN",
                upcr_col="UPCR",
                female_str="Female",
            )

    def test_recognized_sex_is_case_insensitive(self):
        df = pd.DataFrame(
            {
                "SEX": ["FEMALE", "female", "F", "MALE", "male", "M"],
                "DM": [0] * 6,
                "HTN": [0] * 6,
                "UPCR": [500] * 6,
            }
        )
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            res = upcr_uacr(
                df,
                sex_col="SEX",
                diabetes_col="DM",
                hypertension_col="HTN",
                upcr_col="UPCR",
                female_str="Female",
            )
        # No "unrecognized sex" warning should fire for valid, case-insensitive values.
        assert not any("Unrecognized sex" in str(x.message) for x in w)
        # All recognized rows should produce a value.
        assert res.notna().all()

    def test_predict_kfre_unrecognized_sex_row_is_nan(self):
        cols = {
            "age": "Age",
            "sex": "Sex",
            "eGFR": "eGFR",
            "uACR": "uACR",
            "region": "Region",
            "dm": "DM",
            "htn": "HTN",
        }
        df = pd.DataFrame(
            {
                "Age": [60, 60],
                "Sex": ["male", "Femal"],
                "eGFR": [25, 25],
                "uACR": [200, 200],
                "Region": [0, 0],
                "DM": [1, 1],
                "HTN": [1, 1],
            }
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            out = RiskPredictor(df=df, columns=cols).predict_kfre(
                years=2, is_north_american=False
            )
        assert pd.notna(out.iloc[0])  # 'male'
        assert pd.isna(out.iloc[1])  # 'Femal' typo


# ---------------------------------------------------------------------------
# Bug 4 - non-positive uACR: scalar raises, batch warns + NaN
# ---------------------------------------------------------------------------
class TestBug4NonPositiveUacr:
    @pytest.mark.parametrize("bad", [-500, 0, -1e-6])
    def test_scalar_non_positive_raises(self, bad):
        with pytest.raises(ValueError):
            kfre_person(
                age=60,
                is_male=False,
                eGFR=25,
                uACR=bad,
                is_north_american=False,
                years=2,
            )

    def test_valid_scalar_still_works(self):
        r = kfre_person(
            age=60, is_male=False, eGFR=25, uACR=200, is_north_american=False, years=2
        )
        assert 0 <= r <= 1

    def test_batch_bad_uacr_becomes_nan(self):
        df = pd.DataFrame(
            {
                "Age": [60, 70, 55],
                "Sex": ["male", "female", "male"],
                "eGFR": [25, 18, 30],
                "uACR": [200, -500, 0],
                "DM": [1, 0, 1],
                "HTN": [1, 1, 0],
            }
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            out = add_kfre_risk_col(
                df=df,
                age_col="Age",
                sex_col="Sex",
                eGFR_col="eGFR",
                uACR_col="uACR",
                dm_col="DM",
                htn_col="HTN",
                num_vars=[4],
                years=(2,),
                is_north_american=False,
                copy=True,
            )
        col = [c for c in out.columns if c.startswith("kfre")][0]
        assert pd.notna(out[col].iloc[0])  # valid
        assert pd.isna(out[col].iloc[1])  # -500
        assert pd.isna(out[col].iloc[2])  # 0

    def test_batch_warns_on_bad_uacr(self):
        with pytest.warns(UserWarning):
            risk_pred(
                age=np.array([60.0, 70.0]),
                sex=np.array([1.0, 0.0]),
                eGFR=np.array([25.0, 18.0]),
                uACR=np.array([200.0, -500.0]),
                is_north_american=False,
                years=2,
            )


# ---------------------------------------------------------------------------
# Guard: the documented paper result is unchanged by all fixes
# ---------------------------------------------------------------------------
def test_paper_patient_2_unchanged():
    r = kfre_person(
        age=56.88,
        is_male=False,
        eGFR=15,
        uACR=1762.04,
        is_north_american=False,
        years=5,
    )
    assert abs(r - 0.9009) < 5e-4
