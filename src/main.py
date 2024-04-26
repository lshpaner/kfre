import pandas as pd
import numpy as np


class RiskPredictor:
    """
    A class to represent a risk predictor for chronic kidney disease (CKD).

    This class uses the Tangri risk prediction model, which calculates risk
    based on various patient parameters. Results are accurate for both males
    and females, but the original paper calculated risk specifically for males.

    Attributes:
    data (DataFrame): The patient data.
    columns (dict): Dictionary to map expected parameter names to actual column
    names in the data.

    Methods:
    predict(years, use_extra_vars): Predicts the risk of CKD for the given
    number of years, optionally using extra variables for the prediction.
    """

    def __init__(
        self,
        data,
        columns,
    ):
        """
        Constructs the necessary attributes for the RiskPredictor object.

        Parameters:
        data (DataFrame): The patient data.
        columns (dict): A dictionary specifying the column names in the dataset
        that correspond to the required parameters.
        Example: {'age': 'Age', 'sex': 'Gender', 'eGFR': 'eGFR',
        'uACR': 'Albumin_Ratio', 'region': 'Region', 'dm': 'Diabetes',
        'htn': 'Hypertension'}
        apply_conversions (bool, optional): Flag to apply unit conversions.
        Default is False.
        """
        self.data = data
        self.columns = columns

    def perform_conversions(self):
        """
        Applies unit conversions to the biochemical markers in the dataset.

        Converts:
        - uPCR from mmol to mg/g
        - Calcium from mmol to mg/g
        - Phosphate from mmol to mg/g
        - Albumin from g/L to g/dL
        """
        conversion_factor = 1 / 0.11312
        self.data["uPCR (mg/g)"] = self.data[self.columns["uPCR_mmol"]] * conversion_factor
        self.data["Calcium (mg/dL)"] = self.data[self.columns["calcium_mmol"]] * 4
        self.data["Phosphate (mg/dL)"] = self.data[self.columns["phosphate_mmol"]] * 3.1
        self.data["Albumin (g/dL)"] = self.data[self.columns["albumin_g_per_l"]] / 10

    def predict_kfre(self, years, is_north_american, use_extra_vars=False, num_vars=4):
        # Basic required columns
        necessary_cols = [
            self.columns["age"],
            self.columns["sex"],
            self.columns["eGFR"],
            self.columns["uACR"],
        ]

        # Retrieve data only once
        data = self.data[necessary_cols].copy()

        # Convert sex to numeric in a vectorized way
        data[self.columns["sex"]] = (
            data[self.columns["sex"]].str.lower() == "male"
        ).astype(int)

        # Extract basic parameters from the DataFrame
        age = data[self.columns["age"]]
        sex = data[self.columns["sex"]]
        eGFR = data[self.columns["eGFR"]]
        uACR = data[self.columns["uACR"]]

        if use_extra_vars:
            if num_vars == 6:
                # Extend columns for 6-variable model
                necessary_cols.extend([self.columns["dm"], self.columns["htn"]])
                data = self.data[necessary_cols].copy()
                dm = data[self.columns["dm"]]
                htn = data[self.columns["htn"]]
                return risk_pred(
                    age, sex, eGFR, uACR, is_north_american, dm, htn, years=years
                )
            elif num_vars == 8:
                # Extend columns for 8-variable model
                necessary_cols.extend(
                    [
                        self.columns["albumin"],
                        self.columns["phosphorous"],
                        self.columns["bicarbonate"],
                        self.columns["calcium"],
                    ]
                )
                data = self.data[necessary_cols].copy()
                albumin = data[self.columns["albumin"]]
                phosphorous = data[self.columns["phosphorous"]]
                bicarbonate = data[self.columns["bicarbonate"]]
                calcium = data[self.columns["calcium"]]
                return risk_pred(
                    age,
                    sex,
                    eGFR,
                    uACR,
                    is_north_american,
                    None,
                    None,
                    albumin,
                    phosphorous,
                    bicarbonate,
                    calcium,
                    years=years,
                )
        else:
            # Call the function with basic parameters for the 4-variable model
            return risk_pred(age, sex, eGFR, uACR, is_north_american, years=years)


################################################################################
################################ uPCR to uACR ##################################
################################################################################


# Define the generalized conversion function from uPCR to uACR
def uPCR_to_uACR(
    row,
    sex_col,
    diabetes_col,
    hypertension_col,
    uPCR_col,
    female_str,
):
    """
    Converts urinary protein-creatinine ratio (uPCR) to urinary
    albumin-creatinine ratio (uACR) using a specified formula that considers
    patient demographics and conditions.

    Parameters:
    - row (pd.Series): A single row from a pandas DataFrame representing one
      patient's data.
    - sex_col (str): Column name containing the patient's gender.
    - diabetes_col (str): Column name indicating whether the patient has
      diabetes (1 for yes, 0 for no).
    - hypertension_col (str): Column name indicating whether the patient has
      hypertension (1 for yes, 0 for no).
    - uPCR_col (str): Column name containing the urinary protein-creatinine ratio.
    - female_str (str): The exact string used in the dataset to identify a
      patient as female, critical for accurate calculations.

    Returns:
    - float: The computed urinary albumin-creatinine ratio (uACR).

    This function applies a complex logarithmic and exponential calculation to
    derive the uACR from the uPCR, adjusting for factors such as gender,
    diabetes, and hypertension status. The accuracy of the function relies on
    the exact match of the 'female_str' with the dataset's representation of
    female gender.
    """
    uPCR = row[uPCR_col]
    female = 1 if row[sex_col] == female_str else 0
    diabetic = row[diabetes_col]
    hypertensive = row[hypertension_col]

    # Applying the provided formula
    uACR = np.exp(
        5.2659
        + 0.2934 * np.log(np.minimum(uPCR / 50, 1))
        + 1.5643 * np.log(np.maximum(np.minimum(uPCR / 500, 1), 0.1))
        + 1.1109 * np.log(np.maximum(uPCR / 500, 1))
        - 0.0773 * female
        + 0.0797 * diabetic
        + 0.1265 * hypertensive
    )
    return uACR


################################################################################
############################## KFRE Risk Predictor #############################
################################################################################


def risk_pred(
    age,
    sex,
    eGFR,
    uACR,
    is_north_american,  
    dm=None,
    htn=None,
    albumin=None,
    phosphorous=None,
    bicarbonate=None,
    calcium=None,
    years=2,
):
    """
    Calculates the risk of chronic kidney disease progression based on a range 
    of clinical parameters using the Tangri risk prediction model. This model 
    can use 4, 6, or 8 variables for prediction based on the data available. 
    The coefficients and constants used in the calculations are selected based 
    on the geographic region of the patient (North American or not) and the time 
    horizon for the risk prediction (2 or 5 years).

    Parameters:
    - age (float): Age of the patient in years.
    - sex (int): Biological sex of the patient (0 for female, 1 for male).
    - eGFR (float): Estimated Glomerular Filtration Rate, indicating kidney 
      function.
    - uACR (float): Urinary Albumin to Creatinine Ratio, showing kidney damage 
      level.
    - is_north_american (bool): Indicates if the patient is from North America.
    - dm (float, optional): Indicates if the patient has diabetes (0 or 1).
    - htn (float, optional): Indicates if the patient has hypertension (0 or 1).
    - albumin (float, optional): Serum albumin level, required for the 
      8-variable model.
    - phosphorous (float, optional): Serum phosphorous level, required for the 
      8-variable model.
    - bicarbonate (float, optional): Serum bicarbonate level, required for the 
      8-variable model.
    - calcium (float, optional): Serum calcium level, required for the 
      8-variable model.
    - years (int, default=2): The number of years over which the risk is 
      redicted (2 or 5 years).

    Returns:
    - risk_prediction (float): A probability value between 0 and 1 representing 
      the patient's risk of developing chronic kidney disease within the 
      specified number of years.

    Notes:
    The function accounts for the patient's geographic location by adjusting the 
    alpha constants in the risk calculation. It defaults to coefficients for the 
    4-variable model unless additional parameters are provided, in which case it
    switches to the 6-variable or 8-variable models.
    """

    # Alpha values and base risk factors need to be selected based on the model used
    if dm is not None and htn is not None:
        # 6-variable model
        alpha_values = {
            (True, 2): 0.9750,
            (True, 5): 0.9240,
            (False, 2): 0.9830,
            (False, 5): 0.9370,
        }
        base_risk_factors = {
            "age": -0.2201,
            "sex": 0.2467,
            "eGFR": -0.5567,
            "uACR": 0.4510,
        }
    elif (
        albumin is not None
        and phosphorous is not None
        and bicarbonate is not None
        and calcium is not None
    ):
        # 8-variable model
        alpha_values = {
            (True, 2): 0.9780,
            (True, 5): 0.9301,
            (False, 2): 0.9827,
            (False, 5): 0.9245,
        }
        base_risk_factors = {
            "age": -0.1992,
            "sex": 0.1602,
            "eGFR": -0.4919,
            "uACR": 0.3364,
        }
    else:
        # 4-variable model
        alpha_values = {
            (True, 2): 0.9750,
            (True, 5): 0.9240,
            (False, 2): 0.9832,
            (False, 5): 0.9365,
        }
        base_risk_factors = {
            "age": -0.2201,
            "sex": 0.2467,
            "eGFR": -0.5567,
            "uACR": 0.4510,
        }

    # Select alpha based on the patient's region and the number of years
    alpha = alpha_values[(is_north_american, years)]

    # Ensure uACR is positive to avoid log(0)
    uACR = np.maximum(uACR, 1e-6)
    log_uACR = np.log(uACR)

    # Calculate risk factors based on base risk factors for the appropriate model
    risk_factors = (
        base_risk_factors["age"] * (age / 10 - 7.036)
        + base_risk_factors["sex"] * (sex - 0.5642)
        + base_risk_factors["eGFR"] * (eGFR / 5 - 7.222)
        + base_risk_factors["uACR"] * (log_uACR - 5.137)
    )

    # Adjust risk factors for the 6-variable or 8-variable model if necessary
    if dm is not None and htn is not None:
        dm_factor = -0.1475 * (dm - 0.5106)
        htn_factor = 0.1426 * (htn - 0.8501)
        risk_factors += dm_factor + htn_factor

    if (
        albumin is not None
        and phosphorous is not None
        and bicarbonate is not None
        and calcium is not None
    ):
        albumin_factor = -0.3441 * (albumin - 3.997)
        phosph_factor = +0.2604 * (phosphorous - 3.916)
        bicarb_factor = -0.07354 * (bicarbonate - 25.57)
        calcium_factor = -0.2228 * (calcium - 9.355)
        risk_factors += albumin_factor + phosph_factor + bicarb_factor + calcium_factor

    # Compute the risk prediction
    risk_prediction = 1 - alpha ** np.exp(risk_factors)
    return risk_prediction