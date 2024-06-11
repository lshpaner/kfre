################################################################################
############################### Library Imports ################################
import pandas as pd
import numpy as np

################################################################################


class RiskPredictor:
    """
    A class to represent a risk predictor for chronic kidney disease (CKD).

    This class implements the Tangri risk prediction model, which is based on the
    multinational assessments described in Tangri N, Grams ME, Levey AS, et al.
    "Multinational assessment of accuracy of equations for predicting risk of kidney
    failure: A meta-analysis." JAMA, 315(2), 164–174, doi: 10.1001/jama.2015.18202.

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
        df=None,
        columns=None,
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
        self.df = df
        self.columns = columns

    def predict_kfre(
        self,
        years,
        is_north_american,
        use_extra_vars=False,
        num_vars=4,
    ):
        """
        Predicts the risk of chronic kidney disease (CKD) over a specified
        number of years using the Tangri risk prediction model. This method
        supports the basic 4-variable model as well as the extended 6-variable
        and 8-variable models if additional patient data is available.

        Parameters:
        - years (int): The number of years over which the risk assessment is
          projected.
        - is_north_american (bool): Flag indicating whether the patient is from
          North America, which affects the model's constants.
        - use_extra_vars (bool, optional): Determines if additional variables
          (such as diabetes and hypertension status for the 6-variable model, or
          biochemical markers for the 8-variable model) should be used in the
          risk calculation. Defaults to False.
        - num_vars (int, optional): Specifies the number of variables to use in
          the prediction model (4, 6, or 8). Defaults to 4.

        Returns:
        - float: A probability value between 0 and 1 representing the patient's
          risk of CKD development within the specified timeframe.

        Raises:
        - ValueError: If `num_vars` is set to an unsupported number.

        Notes:
        - The 6-variable model includes diabetes and hypertension status in
          addition to the base parameters.
        - The 8-variable model includes serum albumin, phosphorous, bicarbonate,
          and calcium levels in addition to the parameters used in the
          6-variable model.
        - It is important to provide accurate mappings in the `columns`
          dictionary upon class instantiation for the method to correctly locate
          the necessary data in the DataFrame.
        """
        # Basic required columns
        necessary_cols = [
            self.columns["age"],
            self.columns["sex"],
            self.columns["eGFR"],
            self.columns["uACR"],
        ]

        # Retrieve data only once
        df = self.df[necessary_cols].copy()

        # Convert sex to numeric in a vectorized way
        df[self.columns["sex"]] = (
            df[self.columns["sex"]].str.lower() == "male"
        ).astype(int)

        # Extract basic parameters from the DataFrame
        age = df[self.columns["age"]]
        sex = df[self.columns["sex"]]
        eGFR = df[self.columns["eGFR"]]
        uACR = df[self.columns["uACR"]]

        if use_extra_vars:
            if num_vars == 6:
                # Extend columns for 6-variable model
                necessary_cols.extend([self.columns["dm"], self.columns["htn"]])
                df = self.df[necessary_cols].copy()
                dm = df[self.columns["dm"]]
                htn = df[self.columns["htn"]]
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
                df = self.df[necessary_cols].copy()
                albumin = df[self.columns["albumin"]]
                phosphorous = df[self.columns["phosphorous"]]
                bicarbonate = df[self.columns["bicarbonate"]]
                calcium = df[self.columns["calcium"]]
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

    def kfre_person(
        self,
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
        Predicts CKD risk for an individual patient based on provided clinical
        parameters.

        Parameters:
        - age (float): Age of the patient.
        - is_male (bool): True if the patient is male, False if female.
        - eGFR (float): Estimated Glomerular Filtration Rate.
        - uACR (float): Urinary Albumin to Creatinine Ratio.
        - is_north_american (bool): True if the patient is from North America,
          False otherwise.
        - years (int): Time horizon for the risk prediction (default is 2 years).
        - dm (float, optional): Diabetes mellitus indicator (1=yes; 0=no).
        - htn (float, optional): Hypertension indicator (1=yes; 0=no).
        - albumin (float, optional): Serum albumin level.
        - phosphorous (float, optional): Serum phosphorous level.
        - bicarbonate (float, optional): Serum bicarbonate level.
        - calcium (float, optional): Serum calcium level.

        Returns:
        - float: The computed risk of developing CKD.
        """
        errors = []

        if age is None:
            errors.append("Must supply a value for age.")

        if is_male is None:
            errors.append("Must specify sex using True or False for is_male.")

        if eGFR is None:
            errors.append("Must supply a value for eGFR.")

        if uACR is None:
            errors.append("Must supply a value for uACR.")

        if years not in [2, 5]:
            errors.append("Value must be 2 or 5 for 2-year risk or 5-year risk.")

        if dm is not None and dm not in [0, 1, True, False]:
            errors.append("The dm parameter must be either 0, 1, True, or False.")

        if htn is not None and htn not in [0, 1, True, False]:
            errors.append("The htn parameter must be either 0, 1, True, or False.")

        if is_north_american is None:
            errors.append("Must specify True or False for is_north_american.")

        if errors:
            raise ValueError("\n".join(errors))

        # Use is_male directly, since it's already a boolean
        # Call the risk prediction function with the parameters
        risk_prediction = risk_pred(
            age=age,
            sex=is_male,
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
        return risk_prediction


################################################################################
################################ uPCR to uACR ##################################
################################################################################


def upcr_uacr(df, sex_col, diabetes_col, hypertension_col, upcr_col, female_str):
    """
    Converts urinary protein-creatinine ratio (uPCR) to urinary
    albumin-creatinine ratio (uACR) for an entire DataFrame using vectorized
    operations to enhance performance. This function is designed to handle large
    datasets efficiently by applying the conversion formula across columns,
    rather than row-by-row.

    The conversion uses patient-specific factors such as sex, presence of
    diabetes, and presence of hypertension to adjust the uACR calculation
    according to a specified logarithmic and exponential formula. This approach
    is critical in clinical settings where accurate adjustments based on
    demographic factors are essential for proper diagnosis and treatment planning.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the patient data.
    - sex_col (str): Column name in 'df' that contains the patient's gender.
    - diabetes_col (str): Column name in 'df' that indicates whether the
      patient has diabetes (1=yes; 0=no).
    - hypertension_col (str): Column name in 'df' that indicates whether the
      patient has hypertension (1=yes; 0=no).
    - upcr_col (str): Column name in 'df' that contains the urinary
      protein-creatinine ratio.
    - female_str (str): The string used in the dataset to identify female patients.

    Returns:
    - pd.Series: A pandas Series object containing the computed urinary
      albumin-creatinine ratio (uACR) for each patient in the DataFrame.

    This function ensures that all calculations respect the integrity of the
    original data by not modifying any existing columns and only adding the
    resulting uACR as a new column. It handles NaN values by excluding them
    from the calculation, thus retaining them in the resulting uACR values to
    reflect the lack of information for certain patients.

    Notes: Conversion from uPCR to uACR can be independently verified using the
    calculator on `https://ckdpcrisk.org/pcr2acr/`

    This function converts urine protein-creatinine ratio or urine dipstick
    protein to urine albumin-creatinine ratio, based on the method outlined in
    Sumida K, Nadkarni GN, Grams ME, et al. "Conversion of urine protein-creatinine
    ratio or urine dipstick protein to urine albumin-creatinine ratio for use in
    chronic kidney disease screening and prognosis."
    Ann Intern Med, 173(6), 426-435, doi: 10.7326/M20-0529.

    """
    # Convert to float and get the female mask
    upcr = df[upcr_col].astype(float)
    female = (df[sex_col] == female_str).astype(int)

    # Masks to identify valid data for diabetes and hypertension
    diabetic_mask = ~df[diabetes_col].isna()
    hypertensive_mask = ~df[hypertension_col].isna()

    # Only calculate uACR where we have complete information
    valid_mask = diabetic_mask & hypertensive_mask

    # Initialize uACR with NaNs
    uacr = np.full(df.shape[0], np.nan)

    # Calculate uACR only for valid data
    uacr[valid_mask] = np.exp(
        5.2659
        + 0.2934 * np.log(np.minimum(upcr[valid_mask] / 50, 1))
        + 1.5643 * np.log(np.maximum(np.minimum(upcr[valid_mask] / 500, 1), 0.1))
        + 1.1109 * np.log(np.maximum(upcr[valid_mask] / 500, 1))
        - 0.0773 * female[valid_mask]
        + 0.0797 * df[diabetes_col][valid_mask].astype(int)
        + 0.1265 * df[hypertension_col][valid_mask].astype(int)
    )

    return pd.Series(uacr, index=df.index)


################################################################################
#################################  Wrappers  ###################################
################################################################################


# convenience function as wrapper for method with the same name
def predict_kfre(
    df, columns, years, is_north_american, use_extra_vars=False, num_vars=4
):
    """
    A convenience function to predict CKD risk using the Tangri risk prediction
    model without directly creating an instance of the RiskPredictor class.

    Parameters:
    - df (DataFrame): The DataFrame containing patient data.
    - columns (dict): Maps clinical parameter names to DataFrame column names.
    - years (int): Number of years for the risk prediction.
    - is_north_american (bool): True if the data is from North America.
    - use_extra_vars (bool): If True, use additional clinical variables for the
      prediction.
    - num_vars (int): Number of variables used in the model (4, 6, or 8).

    Returns:
    - Series: CKD risk probabilities for each patient.
    """

    predictor = RiskPredictor(df=df, columns=columns)
    return predictor.predict_kfre(
        years=years,
        is_north_american=is_north_american,
        use_extra_vars=use_extra_vars,
        num_vars=num_vars,
    )


def add_kfre_risk_col(
    df,
    age_col=None,
    sex_col=None,
    eGFR_col=None,
    uACR_col=None,
    dm_col=None,
    htn_col=None,
    albumin_col=None,
    phosphorous_col=None,
    bicarbonate_col=None,
    calcium_col=None,
    num_vars=8,
    years=(2, 5),
    is_north_american=False,
    copy=True,
):
    """
    Calculate CKD risks for specified variable num_vars and time frames or for
    all num_vars and years, grouping the results by model first and then by time
    frame in the output DataFrame. Optionally creates a copy of the DataFrame to
    avoid modifying the original data.

    Parameters:
    - df (DataFrame): The patient data.
    - age_col, sex_col, ..., calcium_col (str): Column names for the patient
      parameters.
    - num_vars (int or list): Specifies the number of variables to use (4, 6, 8).
    - years (tuple or list): Time frames to calculate risk for.
    - is_north_american (bool): True if the calculation is for the North
      American region.
    - copy (bool): If True, operates on a copy of the DataFrame. If False,
      modifies the DataFrame in place.

    Returns:
    - DataFrame: The modified or new DataFrame with added risk prediction columns.
    """
    # Use a copy if requested for safety
    df_used = df.copy() if copy else df

    column_map = {
        "age": age_col,
        "sex": sex_col,
        "eGFR": eGFR_col,
        "uACR": uACR_col,
        "dm": dm_col,
        "htn": htn_col,
        "albumin": albumin_col,
        "phosphorous": phosphorous_col,
        "bicarbonate": bicarbonate_col,
        "calcium": calcium_col,
    }

    model_requirements = {
        4: ["age", "sex", "eGFR", "uACR"],
        6: ["age", "sex", "eGFR", "uACR", "dm", "htn"],
        8: [
            "age",
            "sex",
            "eGFR",
            "uACR",
            "albumin",
            "phosphorous",
            "bicarbonate",
            "calcium",
        ],
    }

    # Adjust 'num_vars' and 'years' handling to accept 'all', integer, or iterable
    num_vars = (
        [4, 6, 8]
        if num_vars == "all"
        else ([num_vars] if isinstance(num_vars, int) else num_vars)
    )
    years = (
        [2, 5]
        if years == "all"
        else ([years] if isinstance(years, int) else list(years))
    )

    for model in num_vars:
        missing = [req for req in model_requirements[model] if column_map[req] is None]
        if missing:
            required_cols = ", ".join(missing)
            raise ValueError(
                f"{required_cols} needed to complete calculation for {model}var model"
            )

    # Initialize the predictor with the data and columns
    predictor = RiskPredictor(
        df_used, {k: v for k, v in column_map.items() if v is not None}
    )

    # Calculate risks for each model and time frame
    for model_vars in num_vars:
        if all(column_map[req] is not None for req in model_requirements[model_vars]):
            for time_frame in years:
                risk_column = f"kfre_{model_vars}var_{time_frame}year"
                df_used[risk_column] = predictor.predict_kfre(
                    years=time_frame,
                    is_north_american=is_north_american,
                    use_extra_vars=(model_vars > 4),
                    num_vars=model_vars,
                )

    return df_used


def perform_conversions(
    df,
    reverse=False,
    convert_all=False,
    upcr_col=None,
    calcium_col=None,
    phosphate_col=None,
    albumin_col=None,
):
    """
    Convert specified units of columns in a dataframe and create new columns
    for the results, with specific suffixes based on the conversion direction.
    Original columns are preserved.

    Parameters:
    - df (DataFrame): The dataframe containing the data.
    - reverse (bool): If True, revert to original units by dividing; if False,
      perform the standard conversion by multiplying.
    - convert_all (bool): If True, automatically convert all recognized columns.
    - upcr_col (str, optional): Column name for urine protein-creatinine ratio.
    - calcium_col (str, optional): Column name for calcium.
    - phosphate_col (str, optional): Column name for phosphate.
    - albumin_col (str, optional): Column name for albumin.
    """
    # Define the conversion factors and the suffixes for the converted units
    conversion_factors = {
        "uPCR": 1 / 0.11312,  # From mg/g to mmol/L
        "Calcium": 4,  # From mg/dL to mmol/L
        "Phosphate": 3.1,  # From mg/dL to mmol/L
        "Albumin": 1 / 10,  # From g/dL to g/L
    }

    # Define the suffixes for new column names based on conversion direction
    conversion_suffix = {
        "uPCR": "mg_g" if not reverse else "mmol_L",
        "Calcium": "mg_dl" if not reverse else "mmol_L",
        "Phosphate": "mg_dl" if not reverse else "mmol_L",
        "Albumin": "g_dl" if not reverse else "g_L",
    }

    # Initialize columns_to_convert with provided column names or defaults
    columns_to_convert = {
        "uPCR": upcr_col,
        "Calcium": calcium_col,
        "Phosphate": phosphate_col,
        "Albumin": albumin_col,
    }

    # If convert_all is True, automatically identify columns for conversion
    if convert_all:
        columns_to_convert = {
            key: next((col for col in df.columns if key.lower() in col.lower()), None)
            for key in conversion_factors
        }

    # Perform conversions
    for key, orig_col in columns_to_convert.items():
        if orig_col and orig_col in df.columns:
            factor = conversion_factors[key]
            suffix = conversion_suffix[key]
            # Calculate the converted values
            converted_values = (
                df[orig_col] / factor if reverse else df[orig_col] * factor
            )
            # Create the new column name
            new_col = f"{key}_{suffix}"
            # Add the converted values as a new column to the dataframe
            df[new_col] = converted_values
            print(
                f"Converted '{orig_col}' to new column '{new_col}' with factor {factor}"
            )
        else:
            print(
                f"Warning: Column '{orig_col}' not found in DataFrame. "
                f"No conversion performed for this column."
            )

    return df


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

    # Define the alpha values and risk factor coefficients for each model
    if dm is not None and htn is not None:
        # 6-variable model
        alpha_values = {
            (True, 2): 0.9750,
            (True, 5): 0.9240,
            (False, 2): 0.9830,
            (False, 5): 0.9370,
        }
        risk_factors = {
            "age": -0.2218,  # Adjusted for 6-var model
            "sex": 0.2553,  # Adjusted for 6-var model
            "eGFR": -0.5541,  # Adjusted for 6-var model
            "uACR": 0.4562,  # Adjusted for 6-var model
        }
        dm_factor = -0.1475  # DM risk factor coefficient
        htn_factor = 0.1426  # HTN risk factor coefficient
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
        risk_factors = {
            "age": -0.1992,  # Adjusted for 8-var model
            "sex": 0.1602,  # Adjusted for 8-var model
            "eGFR": -0.4919,  # Adjusted for 8-var model
            "uACR": 0.3364,  # Adjusted for 8-var model
        }
        # Extra risk factors for the 8-variable model
        albumin_factor = -0.3441
        phosph_factor = +0.2604
        bicarb_factor = -0.07354
        calcium_factor = -0.2228
    else:
        # 4-variable model
        alpha_values = {
            (True, 2): 0.9750,
            (True, 5): 0.9240,
            (False, 2): 0.9832,
            (False, 5): 0.9365,
        }
        risk_factors = {
            "age": -0.2201,
            "sex": 0.2467,
            "eGFR": -0.5567,
            "uACR": 0.4510,
        }

    # Ensure uACR is positive to avoid log(0)
    uACR = np.maximum(uACR, 1e-6)
    log_uACR = np.log(uACR)

    # Compute the base risk score using the coefficients
    risk_score = (
        risk_factors["age"] * (age / 10 - 7.036)
        + risk_factors["sex"] * (sex - 0.5642)
        + risk_factors["eGFR"] * (eGFR / 5 - 7.222)
        + risk_factors["uACR"] * (log_uACR - 5.137)
    )

    # Adjust risk score for the 6-variable model if DM and HTN data is provided
    if dm is not None and htn is not None:
        risk_score += dm_factor * (dm - 0.5106) + htn_factor * (htn - 0.8501)

    # Adjust risk score for the 8-variable model if additional data is provided
    if (
        albumin is not None
        and phosphorous is not None
        and bicarbonate is not None
        and calcium is not None
    ):
        risk_score += (
            albumin_factor * (albumin - 3.997)
            + phosph_factor * (phosphorous - 3.916)
            + bicarb_factor * (bicarbonate - 25.57)
            + calcium_factor * (calcium - 9.355)
        )

    # Select alpha based on region and years
    alpha = alpha_values[(is_north_american, years)]

    # Compute the risk prediction
    risk_prediction = 1 - alpha ** np.exp(risk_score)
    return risk_prediction


################################################################################
# References
# ------------------------------------------------------------------------------
#
# Tangri N, Grams ME, Levey AS, Coresh J, et al. (2016). Multinational assessment
# of accuracy of equations for predicting risk of kidney failure: A meta-analysis.
# JAMA, 315(2), 164–174. doi: 10.1001/jama.2015.18202.
#
# Tangri, N., Stevens, L. A., Griffith, J., Tighiouart, H., Djurdjev, O.,
# Naimark, D., Levin, A., & Levey, A. S. (2011). A predictive model for
# progression of chronic kidney disease to kidney failure. JAMA, 305(15),
# 1553-1559. doi: 10.1001/jama.2011.451.
#
# Sumida K, Nadkarni GN, Grams ME, Sang Y, et al. (2020). Conversion of urine
# protein-creatinine ratio or urine dipstick protein to urine albumin-creatinine
# ratio for use in chronic kidney disease screening and prognosis. Ann Intern Med,
# 173(6), 426-435. doi: 10.7326/M20-0529.
# ------------------------------------------------------------------------------
################################################################################
