__version__ = "0.1.8"

from .main import (
    RiskPredictor,
    upcr_uacr,
    risk_pred,
    predict_kfre,
    perform_conversions,
    add_kfre_risk_col,
)


def kfre_person(
    age,
    is_male,
    eGFR,
    uACR,
    is_north_american,
    years=2,
    dm=None,
    htn=None,
    albumin=None,
    phosphorous=None,
    bicarbonate=None,
    calcium=None,
):
    """
    Direct function to predict CKD risk for an individual using specific clinical
    parameters.

    :param age: Age of the patient.
    :param is_male: True if the patient is male, False if female.
    :param eGFR: Estimated Glomerular Filtration Rate.
    :param uACR: Urinary Albumin to Creatinine Ratio.
    :param is_north_american: True if the patient is from North America,
     otherwise False.
    :param years: Time horizon for the risk prediction (default is 2 years).
    :param dm: Diabetes mellitus indicator (1=yes; 0=no), optional.
    :param htn: Hypertension indicator (1=yes; 0=no), optional.
    :param albumin: Serum albumin level, optional.
    :param phosphorous: Serum phosphorous level, optional.
    :param bicarbonate: Serum bicarbonate level, optional.
    :param calcium: Serum calcium level, optional.
    :return: The computed risk of developing CKD.
    """
    predictor = RiskPredictor()
    return predictor.kfre_person(
        age=age,
        is_male=is_male,
        eGFR=eGFR,
        uACR=uACR,
        is_north_american=is_north_american,
        years=years,
        dm=dm,
        htn=htn,
        albumin=albumin,
        phosphorous=phosphorous,
        bicarbonate=bicarbonate,
        calcium=calcium,
    )


# Export the RiskPredictor class for direct use
__all__ = [
    "kfre_person",
    "upcr_uacr",
    "predict_kfre",
    "perform_conversions",
    "add_kfre_risk_col",
    "RiskPredictor",
]
