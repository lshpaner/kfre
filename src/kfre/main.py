################################################################################
############################### Library Imports ################################
from .perform_eval import *

################################################################################


class RiskPredictor:
    """
    A class to represent a kidney failure risk predictor for patients with
    chronic kidney disease (CKD).

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
    predict(years, use_extra_vars): Predicts the risk of kidney failure for the
    givennumber of years, optionally using extra variables for the prediction.
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
        precision=None,
    ):
        """
        Predicts the risk of kidney failure in a patient with chronic kidney
        disease over a specified number of years using the Tangri Kidney
        Failure Risk Equation (KFRE). This method supports the basic 4-variable
        model as well as the extended 6-variable and 8-variable models if
        additional patient data is available.

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
          risk of kidney failure within the specified timeframe. Rows with an
          unrecognized or missing sex value are returned as NaN.

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

        # Resolve sex robustly: recognized female/male map to 0/1; unrecognized
        # values warn and are marked invalid so they yield NaN rather than being
        # silently coerced. (1 - female) gives the male=1 encoding used below.
        female_flag, sex_valid = _resolve_sex_series(df[self.columns["sex"]])
        df[self.columns["sex"]] = (1 - female_flag).astype(int)

        # Extract basic parameters from the DataFrame
        age = df[self.columns["age"]]
        sex = df[self.columns["sex"]]
        eGFR = df[self.columns["eGFR"]]
        uACR = df[self.columns["uACR"]]

        # Validate num_vars up front so unsupported values fail loudly
        # instead of silently returning None.
        if num_vars not in (4, 6, 8):
            raise ValueError(f"num_vars must be 4, 6, or 8; got {num_vars!r}.")

        if use_extra_vars and num_vars == 6:
            # Extend columns for 6-variable model
            necessary_cols.extend([self.columns["dm"], self.columns["htn"]])
            df = self.df[necessary_cols].copy()
            dm = df[self.columns["dm"]]
            htn = df[self.columns["htn"]]
            result = apply_precision(
                risk_pred(
                    age,
                    sex,
                    eGFR,
                    uACR,
                    is_north_american,
                    dm,
                    htn,
                    years=years,
                ),
                precision=precision,
            )
        elif use_extra_vars and num_vars == 8:
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
            result = apply_precision(
                risk_pred(
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
                ),
                precision=precision,
            )
        else:
            # 4-variable model. Covers use_extra_vars=False, and the explicit
            # use_extra_vars=True with num_vars=4 case.
            result = apply_precision(
                risk_pred(age, sex, eGFR, uACR, is_north_american, years=years),
                precision=precision,
            )

        # Rows with an unrecognized/missing sex value get NaN rather than a
        # prediction based on a silently coerced sex.
        result = pd.Series(result, index=self.df.index)
        result[~sex_valid.to_numpy()] = np.nan
        return result

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
        precision=None,
    ):
        """
        Predicts kidney failure risk for an individual patient based on provided
        clinical parameters.

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
        - precision (int, optional): Number of decimal places to round the
          predicted risk to. If None, no rounding is applied.

        Returns:
        - float: The computed risk of kidney failure.
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
        return apply_precision(risk_prediction, precision=precision)


###############################################################################
# Precision helper
###############################################################################


def apply_precision(result, precision=None):
    """
    Optionally round numeric outputs to a given number of decimal places.
    Works with scalars, numpy arrays, pandas Series, and DataFrames.
    Returns the same type where possible.
    """
    if precision is None:
        return result

    # scalar numbers
    if isinstance(result, (int, float)):
        return round(result, precision)

    # numpy arrays, pandas Series/DataFrame expose .round
    if hasattr(result, "round"):
        return result.round(precision)

    # generic iterables fallback
    try:
        return type(result)(round(x, precision) for x in result)
    except Exception:
        return result


################################################################################
################################# Sex Helper ###################################
################################################################################


def _resolve_sex_series(sex_series, female_str=None):
    """
    Robustly resolve a sex column into a female indicator and a validity mask.

    Recognized values are matched case-insensitively: female {"female", "f"}
    and male {"male", "m"}. If ``female_str`` is provided, that exact label is
    also accepted as female (case-insensitively). Any non-empty value that is
    not recognized (e.g. typos, "unknown") triggers a warning and is marked
    invalid; genuinely missing values (NaN, empty) are marked invalid quietly.

    Returns
    -------
    (female_flag, valid_mask) : (pd.Series[int], pd.Series[bool])
        ``female_flag`` is 1 for female, 0 otherwise (0 is meaningless where
        ``valid_mask`` is False). ``valid_mask`` is True only for rows with a
        recognized sex value.
    """
    import warnings

    female_tokens = {"female", "f"}
    male_tokens = {"male", "m"}
    if female_str is not None:
        female_tokens = female_tokens | {str(female_str).strip().lower()}

    normalized = sex_series.astype("string").str.strip().str.lower()

    female_flag = normalized.isin(female_tokens)
    male_flag = normalized.isin(male_tokens)
    valid_mask = female_flag | male_flag

    # Warn about non-empty values that were not recognized (data-quality issue),
    # but stay quiet about genuinely missing entries.
    non_empty = normalized.notna() & (normalized.str.len() > 0)
    unrecognized = non_empty & ~valid_mask
    if unrecognized.any():
        bad = sorted(set(sex_series[unrecognized].astype(str)))
        warnings.warn(
            "Unrecognized sex value(s) "
            f"{bad} were treated as missing (result set to NaN). "
            "Recognized values are female/f and male/m "
            "(case-insensitive).",
            UserWarning,
            stacklevel=2,
        )

    return female_flag.astype(int), valid_mask


################################################################################
################################ uPCR to uACR ##################################
################################################################################


def upcr_uacr(df, sex_col, diabetes_col, hypertension_col, upcr_col, female_str):
    """
    Estimate the urinary albumin-creatinine ratio (uACR) from the urinary
    protein-creatinine ratio (uPCR) for an entire DataFrame using vectorized
    operations. This function is designed to handle large datasets efficiently
    by applying the conversion formula across columns, rather than row-by-row.

    The conversion uses patient-specific factors such as sex, presence of
    diabetes, and presence of hypertension to adjust the uACR estimate
    according to a specified logarithmic and exponential formula.

    IMPORTANT: The uPCR-to-uACR conversion is an APPROXIMATION, not a
    measurement. The albumin fraction of total urinary protein varies between
    individuals (and with the underlying cause of proteinuria), so there is no
    universally agreed conversion, and estimated uACR values carry inherent
    measurement error. A directly measured uACR should always be preferred when
    available; converted values should be interpreted with caution, and this
    limitation should be reported wherever converted uACR is used. A runtime
    warning is emitted whenever this function produces estimated values.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the patient data.
    - sex_col (str): Column name in 'df' that contains the patient's sex.
    - diabetes_col (str): Column name in 'df' that indicates whether the
      patient has diabetes (1=yes; 0=no).
    - hypertension_col (str): Column name in 'df' that indicates whether the
      patient has hypertension (1=yes; 0=no).
    - upcr_col (str): Column name in 'df' that contains the urinary
      protein-creatinine ratio.
    - female_str (str): The string used in the dataset to identify female patients.

    Returns:
    - pd.Series: A pandas Series object containing the estimated urinary
      albumin-creatinine ratio (uACR) for each patient in the DataFrame.

    This function ensures that all calculations respect the integrity of the
    original data by not modifying any existing columns and only returning the
    resulting uACR as a new Series. It handles NaN values by excluding them
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
    import warnings

    # Convert to float and resolve sex robustly. Recognized female/male values
    # are mapped explicitly; anything unrecognized (typos, "unknown", blanks)
    # is treated as missing so it yields NaN rather than being silently coerced
    # into a valid-looking prediction.
    upcr = df[upcr_col].astype(float)
    female_flag, sex_valid = _resolve_sex_series(df[sex_col], female_str)

    # Masks to identify valid data for diabetes and hypertension
    diabetic_mask = ~df[diabetes_col].isna()
    hypertensive_mask = ~df[hypertension_col].isna()

    # Only calculate uACR where we have complete information (including a
    # recognized sex value)
    valid_mask = diabetic_mask & hypertensive_mask & sex_valid

    # Initialize uACR with NaNs
    uacr = np.full(df.shape[0], np.nan)

    # Calculate uACR only for valid data
    uacr[valid_mask.to_numpy()] = np.exp(
        5.2659
        + 0.2934 * np.log(np.minimum(upcr[valid_mask] / 50, 1))
        + 1.5643 * np.log(np.maximum(np.minimum(upcr[valid_mask] / 500, 1), 0.1))
        + 1.1109 * np.log(np.maximum(upcr[valid_mask] / 500, 1))
        - 0.0773 * female_flag[valid_mask]
        + 0.0797 * df[diabetes_col][valid_mask].astype(int)
        + 0.1265 * df[hypertension_col][valid_mask].astype(int)
    )

    # Disclaimer on the software output: values are estimated, not measured.
    if bool(valid_mask.any()):
        warnings.warn(
            "uACR values were ESTIMATED from uPCR using the Sumida et al. "
            "(2020) conversion. This conversion is an approximation without "
            "universal consensus and carries inherent measurement error; "
            "prefer a measured uACR when available and report this limitation "
            "wherever converted values are used.",
            UserWarning,
            stacklevel=2,
        )

    return pd.Series(uacr, index=df.index)


################################################################################
#################################  Wrappers  ###################################
################################################################################


# convenience function as wrapper for method with the same name
def predict_kfre(
    df,
    columns,
    years,
    is_north_american,
    use_extra_vars=False,
    num_vars=4,
    precision=None,
):
    """
    A convenience function to predict kidney failure risk using the Tangri risk
    prediction

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
        precision=precision,
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
    precision=None,
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
                df_used[risk_column] = apply_precision(
                    predictor.predict_kfre(
                        years=time_frame,
                        is_north_american=is_north_american,
                        use_extra_vars=(model_vars > 4),
                        num_vars=model_vars,
                    ),
                    precision=precision,
                )

    return df_used


################################################################################


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
    Convert specified laboratory columns between SI and conventional units,
    adding new columns and preserving the originals.

    Direction:
    - reverse=False (default): SI -> conventional units, i.e.
      uPCR mg/mmol -> mg/g, calcium mmol/L -> mg/dL,
      phosphate mmol/L -> mg/dL, albumin g/L -> g/dL.
      These are the conventional units expected by the KFRE.
    - reverse=True: the inverse conversion (conventional -> SI).

    Conversion factors (applied by multiplication when reverse=False):
      uPCR x1/0.11312 (~8.84), calcium x4, phosphate x3.1, albumin x0.1.

    Parameters:
    - df (DataFrame): The dataframe containing the data.
    - reverse (bool): If True, convert from conventional -> SI units; if False,
      convert from SI -> conventional units.
    - convert_all (bool): If True, automatically identify columns for conversion.
    - upcr_col (str, optional): Column name for urine protein-creatinine ratio.
    - calcium_col (str, optional): Column name for calcium.
    - phosphate_col (str, optional): Column name for phosphate.
    - albumin_col (str, optional): Column name for albumin.
    """
    # Conversion factors verified against standard reference values
    # (molar masses / standard SI<->conventional factors):
    #   Calcium:   1 mmol/L = 4.0 mg/dL    (MW 40.08; x4)
    #   Phosphate: 1 mmol/L = 3.1 mg/dL    (MW ~31; x3.1)
    #   Albumin:   1 g/L    = 0.1 g/dL     (x0.1)
    #   uPCR:      mg/mmol  -> mg/g  via 1 mmol creatinine = 0.11312 g
    #              (creatinine MW 113.12; x 1/0.11312 ~= 8.8401)

    conversion_factors = {
        "uPCR": 1 / 0.11312,
        "Calcium": 4,
        "Phosphate": 3.1,
        "Albumin": 1 / 10,
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

    # If convert_all is True, automatically identify columns for conversion by
    # name. NOTE: convert_all is intended for a single pass over a frame of raw
    # input values. To reverse a conversion, pass the specific converted column
    # names explicitly (e.g. calcium_col="Calcium_mg_dl") rather than relying on
    # convert_all, which cannot disambiguate an original column from its own
    # converted output when both are present.
    if convert_all:
        columns_to_convert = {
            key: next((col for col in df.columns if key.lower() in col.lower()), None)
            for key in conversion_factors
        }

    # Create a deep copy of the DataFrame
    df = df.copy()

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
            # Add the converted values as a new column to the dataframe using
            # .loc to avoid SettingWithCopyWarning
            df.loc[:, new_col] = converted_values
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


def _warn_out_of_bounds(
    age=None,
    eGFR=None,
    uACR=None,
    albumin=None,
    phosphorous=None,
    bicarbonate=None,
    calcium=None,
    model=4,
):
    """
    Emit a UserWarning when covariates fall outside broad, physiologically
    plausible ranges for the KFRE (adults with CKD stages G3-G5). Conservative
    scope checks only: values are not modified and predictions are still
    returned; the warning flags possible extrapolation. Works for scalar or
    array-like inputs.
    """
    import warnings

    # (name, value, low, high) using inclusive bounds. Ranges are intentionally
    # broad so the check flags clear out-of-scope values, not borderline ones.
    checks = [
        ("age", age, 18, 100),  # adult population
        ("eGFR", eGFR, 0, 60),  # KFRE scope: CKD G3-G5 (eGFR < 60)
        ("uACR", uACR, 0, 25000),  # mg/g; upper guard against implausible entries
    ]
    if model == 8:
        checks += [
            ("albumin", albumin, 1.0, 6.0),  # g/dL
            ("phosphorous", phosphorous, 1.0, 10.0),  # mg/dL
            ("bicarbonate", bicarbonate, 5.0, 45.0),  # mEq/L
            ("calcium", calcium, 5.0, 15.0),  # mg/dL
        ]

    offenders = []
    for name, val, low, high in checks:
        if val is None:
            continue
        arr = np.asarray(val, dtype=float)
        with np.errstate(invalid="ignore"):
            out = (arr < low) | (arr > high)
        # ignore NaNs (handled elsewhere); only flag real out-of-range values
        out = np.where(np.isnan(arr), False, out)
        if np.any(out):
            offenders.append(f"{name} (expected {low}-{high})")

    if offenders:
        warnings.warn(
            "One or more covariates fall outside the KFRE's intended range: "
            + "; ".join(offenders)
            + ". Predictions are still returned but may be unreliable for "
            "values outside the model's development population "
            "(adults, CKD stages G3-G5).",
            UserWarning,
            stacklevel=2,
        )


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
    num_vars=None,
):
    """
    Calculates the risk of kidney failure in a patient with chronic kidney
    disease using the Tangri Kidney Failure Risk Equation (KFRE). Three distinct
    published models are supported (4-, 6-, and 8-variable); the appropriate
    model is selected from the inputs provided, and its published coefficients
    and baseline survival are applied for the requested region and horizon.

    Model selection
    ---------------
    The 4-, 6-, and 8-variable KFRE are separate published models, each with its
    own coefficients and baseline survival. When inputs for more than one model
    are supplied, the library uses the variant with the most variables
    (8 > 6 > 4), i.e. the most information-rich model the provided data support.
    Pass ``num_vars`` (4, 6, or 8) to select a specific model explicitly; a
    ``ValueError`` is raised if the inputs required by the requested model are
    not all present.

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
      predicted (2 or 5 years).
    - num_vars (int, optional): Force a specific KFRE variant (4, 6, or 8).
      When None (default), the variant is inferred using 8 > 6 > 4 precedence.

    Returns:
    - risk_prediction (float): A probability value between 0 and 1 representing
      the patient's risk of kidney failure within the specified number of years.

    Raises:
    - ValueError: If ``num_vars`` is not one of 4, 6, or 8, or if the inputs
      required by the selected model are not all provided.
    """

    # Which optional input groups are fully available.
    has_6var = dm is not None and htn is not None
    has_8var = (
        albumin is not None
        and phosphorous is not None
        and bicarbonate is not None
        and calcium is not None
    )

    # Resolve which model to use: explicit override, else 8 > 6 > 4 precedence.
    if num_vars is None:
        if has_8var:
            model = 8
        elif has_6var:
            model = 6
        else:
            model = 4
    else:
        if num_vars not in (4, 6, 8):
            raise ValueError(f"num_vars must be 4, 6, or 8; got {num_vars!r}.")
        if num_vars == 8 and not has_8var:
            raise ValueError(
                "The 8-variable model requires albumin, phosphorous, "
                "bicarbonate, and calcium."
            )
        if num_vars == 6 and not has_6var:
            raise ValueError("The 6-variable model requires dm and htn.")
        model = num_vars

    # Warn if covariates fall outside broad, physiologically plausible ranges
    # for which the KFRE (developed on CKD stages G3-G5 in adults) is intended.
    # These are conservative scope checks, not the equation's exact validation
    # envelope; predictions for out-of-range values are still returned but may
    # be unreliable because the model is linear and extrapolates poorly.
    _warn_out_of_bounds(
        age=age,
        eGFR=eGFR,
        uACR=uACR,
        albumin=albumin,
        phosphorous=phosphorous,
        bicarbonate=bicarbonate,
        calcium=calcium,
        model=model,
    )

    # Define the alpha values and risk factor coefficients for the chosen model.
    if model == 6:
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
    elif model == 8:
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
    # uACR is a strictly positive ratio; non-positive values (<= 0) are
    # invalid and must not be silently rescued into a valid-looking result.
    # Scalar input: raise. Array/Series input: warn and set the offending
    # entries to NaN so a single bad row does not abort a whole cohort.
    uACR = np.asarray(uACR, dtype=float)
    invalid = uACR <= 0
    if np.ndim(uACR) == 0:
        if bool(invalid):
            raise ValueError(f"uACR must be positive; got {float(uACR)}.")
        log_uACR = np.log(uACR)
    else:
        if invalid.any():
            import warnings

            n_bad = int(invalid.sum())
            warnings.warn(
                f"{n_bad} uACR value(s) were non-positive and set to NaN "
                "(uACR must be > 0).",
                UserWarning,
                stacklevel=2,
            )
        safe = np.where(invalid, np.nan, uACR)
        log_uACR = np.log(safe)

    # Compute the base risk score using the coefficients
    risk_score = (
        risk_factors["age"] * (age / 10 - 7.036)
        + risk_factors["sex"] * (sex - 0.5642)
        + risk_factors["eGFR"] * (eGFR / 5 - 7.222)
        + risk_factors["uACR"] * (log_uACR - 5.137)
    )

    # Adjust risk score for the 6-variable model
    if model == 6:
        risk_score += dm_factor * (dm - 0.5106) + htn_factor * (htn - 0.8501)

    # Adjust risk score for the 8-variable model
    if model == 8:
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
