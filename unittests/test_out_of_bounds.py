import warnings, numpy as np, pandas as pd, pytest
from kfre import kfre_person, add_kfre_risk_col


def _warnings(fn):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        fn()
        return [str(x.message) for x in w if issubclass(x.category, UserWarning)]


def _oob(msgs, name):
    return any("intended range" in m and name in m for m in msgs)


class TestOutOfBoundsWarnings:
    def test_in_range_no_warning(self):
        msgs = _warnings(
            lambda: kfre_person(
                age=60,
                is_male=False,
                eGFR=25,
                uACR=200,
                is_north_american=False,
                years=2,
            )
        )
        assert not any("intended range" in m for m in msgs)

    def test_egfr_above_scope_warns(self):
        msgs = _warnings(
            lambda: kfre_person(
                age=60,
                is_male=False,
                eGFR=80,
                uACR=200,
                is_north_american=False,
                years=2,
            )
        )
        assert _oob(msgs, "eGFR")

    def test_age_below_adult_warns(self):
        msgs = _warnings(
            lambda: kfre_person(
                age=12,
                is_male=False,
                eGFR=25,
                uACR=200,
                is_north_american=False,
                years=2,
            )
        )
        assert _oob(msgs, "age")

    def test_biochem_out_of_range_warns_only_in_8var(self):
        msgs = _warnings(
            lambda: kfre_person(
                age=60,
                is_male=False,
                eGFR=25,
                uACR=200,
                is_north_american=False,
                years=2,
                albumin=3.5,
                phosphorous=99,
                bicarbonate=24,
                calcium=9.0,
            )
        )
        assert _oob(msgs, "phosphorous")

    def test_prediction_still_returned_when_out_of_range(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = kfre_person(
                age=60,
                is_male=False,
                eGFR=80,
                uACR=200,
                is_north_american=False,
                years=2,
            )
        assert np.isfinite(r)

    def test_batch_out_of_range_row_warns(self):
        df = pd.DataFrame(
            {
                "Age": [60, 60],
                "Sex": ["male", "female"],
                "eGFR": [25, 200],
                "uACR": [200, 200],
                "DM": [1, 0],
                "HTN": [1, 1],
            }
        )
        msgs = _warnings(
            lambda: add_kfre_risk_col(
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
        )
        assert _oob(msgs, "eGFR")

    def test_paper_patient_unaffected(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = kfre_person(
                age=56.88,
                is_male=False,
                eGFR=15,
                uACR=1762.04,
                is_north_american=False,
                years=5,
            )
        assert abs(r - 0.9009) < 5e-4
