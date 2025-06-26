import pytest
from kfre import kfre_person


@pytest.mark.parametrize("years,expected_range", [(2, (0, 1)), (5, (0, 1))])
def test_kfre_person_basic(years, expected_range):
    val = kfre_person(
        age=57.28,
        is_male=False,
        eGFR=15.0,
        uACR=1762.00184,
        is_north_american=False,
        years=years,
        dm=None,
        htn=None,
        albumin=None,
        phosphorous=None,
        bicarbonate=None,
        calcium=None,
    )
    assert isinstance(val, float)
    low, high = expected_range
    assert low <= val <= high
