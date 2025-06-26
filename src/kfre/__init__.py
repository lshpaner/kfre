import sys
import builtins
from .logo import *

from .perform_eval import *
from .main import *


detailed_doc = """
Kidney Failure Risk Equation (KFRE) Python Library
========================================================================================

`kfre` is a Python library designed to estimate the risk of chronic kidney disease 
(CKD) progression over two distinct timelines: 2 years and 5 years. Using Tangri's 
Kidney Failure Risk Equation (KFRE), the library provides tools for healthcare 
professionals and researchers to predict CKD risk based on patient data. It supports 
predictions for both males and females and includes specific adjustments for individuals 
from North American and non-North American regions.

PyPI: https://pypi.org/project/kfre/
Documentation: https://lshpaner.github.io/kfre/

Version: 0.1.13

"""

__author__ = "Leonid Shpaner"
__email__ = "lshpaner@ucla.edu"
__version__ = "0.1.13"


# Define the custom help function
def custom_help(obj=None):
    """
    Custom help function to dynamically include ASCII art in help() output.
    """
    if (
        obj is None or obj is sys.modules[__name__]
    ):  # When `help()` is called for this module
        print(kfre_logo)  # Print ASCII art first
        print(detailed_doc)  # Print the detailed documentation
    else:
        original_help(obj)  # Use the original help for other objects


# Backup the original help function
original_help = builtins.help

# Override the global help function in builtins
builtins.help = custom_help


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
