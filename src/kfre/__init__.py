"""

888    d8P  8888888888 8888888b.  8888888888
888   d8P   888        888   Y88b 888
888  d8P    888        888    888 888
888d88K     8888888    888   d88P 8888888
8888888b    888        8888888P"  888
888  Y88b   888        888 T88b   888
888   Y88b  888        888  T88b  888
888    Y88b 888        888   T88b 8888888888

Kidney Failure Risk Equation (KFRE) Python Library
===================================================

This library provides tools to compute CKD risk based on clinical parameters,
using the Kidney Failure Risk Equation (KFRE). It includes functions for individual
risk prediction, data conversion, and evaluation of KFRE metrics.


"""

__author__ = "Leonid Shpaner"
__email__ = "lshpaner@ucla.edu"
__version__ = "0.1.12"


from .perform_eval import *
from .main import *


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


# Export functions for direct use
__all__ = [
    "kfre_person",
    "upcr_uacr",
    "predict_kfre",
    "perform_conversions",
    "add_kfre_risk_col",
    "RiskPredictor",
    "class_esrd_outcome",
    "class_ckd_stages",
    "plot_kfre_metrics",
    "eval_kfre_metrics",
]
