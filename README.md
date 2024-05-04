# KFRE: Kidney Failure Risk Estimator

[![PyPI](https://img.shields.io/pypi/v/kfre.svg)](https://pypi.org/project/kfre/)
[![Downloads](https://pepy.tech/badge/kfre)](https://pepy.tech/project/kfre)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/lshpaner/kfre/tree/main?tab=License-1-ov-file)
[![Zenodo](https://zenodo.org/badge/DOI/10.5281/zenodo.11100223.svg)](https://doi.org/10.5281/zenodo.11100222)

`kfre` is a Python library designed to estimate the risk of chronic kidney disease (CKD) progression over two distinct timelines: 2 years and 5 years. Using Tangri's Kidney Failure Risk Equation (KFRE), the library provides tools for healthcare professionals and researchers to predict CKD risk based on patient data. It supports predictions for both males and females and includes specific adjustments for individuals from North American and non-North American regions.

--------
## Table of Contents

1. [Features](#Features)
2. [Prerequisites](#Prerequisites)
3. [Installation](#installation)
4. [Usage Guide](#usage-guide)
   - [Single Patient Risk Calculation](#single-patient-risk-calculation)
   - [Batch Risk Calculation for Multiple Patients](#batch-risk-calculation-for-multiple-patients)
   - [Conversion of Clinical Parameters](#conversion-of-clinical-parameters)
        - [uPCR to uACR](#upcr-to-uacr)
        - [Calcium](#calcium)
        - [Phosphate](#phosphate)
        - [Albumin](#albumin)
5. [Contributor/Maintainer](#contributormaintainer)
6. [License](#license)
7. [Support](#acknowledgements)
8. [References](#references)
--------


## Features

- **Risk Prediction**: Utilize Tangri's validated risk prediction model to estimate kidney failure risk using
    - 4 variables: sex, age, eGFR, uACR (log-normalized)
    - 6 variables: sex, age, eGFR, uACR (log-normalized), diabetes mellitus, hypertension
    - 8 variables: sex, age, eGFR, uACR (log-normalized), serum albumin, serum phosphorous, serum calcium, and serum bicarbonate.
- **Data Flexibility**: Handles various input data formats and maps them to required model parameters.
- **Conversion Utilities**: Includes functions to convert common laboratory results to the required units for risk prediction.

### Important Note on Data Units
The kfre library requires precise data input, with clear specification of the units for each variable. The variables can be expressed in multiple units, and it's crucial that the data being used clearly delineates which units the variables are expressed in. For instance:

- uACR (Urinary Albumin-Creatinine Ratio) can be expressed in either mg/g or mg/mmol.
- Albumin levels can be measured in g/dL or g/L.
- Phosphorous levels can be noted in mg/dL or mmol/L.
- Bicarbonate can be recorded in mEq/L or mmol/L.
- Calcium can be documented in mg/dL or mmol/L.

This flexibility allows the library to be used with a variety of clinical data sources, enhancing its applicability across different healthcare settings.

## Prerequisites
Before you install `kfre`, ensure you have the following:

- **Python**: Python 3.6 or higher is required to run `kfre`.

Additionally, kfre has the following package dependencies:

- **NumPy**: Version 1.18.5 or higher
- **Pandas**: Version 1.0.5 or higher

These dependencies will be automatically installed when you install kfre using pip.

## Installation

You can install `kfre` directly from PyPI:

```bash
pip install kfre
```

## Usage Guide

## Single Patient Risk Calculation
The kfre library offers a flexible and user-friendly interface to estimate the risk of kidney failure for individual patients using Tangri's KFRE model. With `kfre`, you can calculate the risk using the classic 4-variable model, the detailed 8-variable model, and, uniquely, a 6-variable model that is not commonly found in online calculators.

## `kfre_person`

```python
risk_percentage = kfre_person(
    age=57.28,
    is_male=False,
    eGFR=15.0,
    uACR=1762.001840,
    is_north_american=False,
    years=2,
    dm=None,
    htn=None,
    albumin=None,
    phosphorous=None,
    bicarbonate=None,
    calcium=None
) * 100  # Convert to percentage

```

Parameters: 

- `age` (float): The age of the patient in years.
- `is_male` (bool): Indicates if the patient is male. False indicates a female patient.
- `eGFR` (float): Estimated Glomerular Filtration Rate in mL/min/1.73 m², indicating kidney function.
- `uACR` (float): Urinary Albumin to Creatinine Ratio in mg/g, indicating kidney damage.
- `is_north_american` (bool): Specifies whether the patient is from North America, affecting model constants.
- `years` (int): The time frame in years (2 or 5) over which the risk assessment is projected.
- `dm` (float, optional): Diabetes mellitus status (1 if present, 0 if not). Required for the 6-variable model.
- `htn` (float, optional): Hypertension status (1 if present, 0 if not). Required for the 6-variable model.
- `albumin` (float, optional): Serum albumin level in g/dL. Required for the 8-variable model.
- `phosphorous` (float, optional): Serum phosphorus level in mg/dL. Required for the 8-variable model.
- `bicarbonate` (float, optional): Serum bicarbonate level in mEq/L. Required for the 8-variable model.
- `calcium` (float, optional): Serum calcium level in mg/dL. Required for the 8-variable model.

Returns:

`float`: The risk of developing CKD within the specified timeframe, as a decimal. Multiply by 100 to convert to a percentage.

Description:

The `kfre_person` function allows for detailed, personalized risk assessments based on a range of clinical parameters. Depending on the completeness of the data provided, the function can apply a basic 4-variable model or more comprehensive models incorporating additional risk factors like diabetes, hypertension, and various biochemical markers.

The function is designed for ease of use in clinical settings or research, providing immediate risk estimations that are crucial for patient management or further analysis.

### Example Calculation for 2-year and 5-year Risk
Here's how to estimate the 2-year and 5-year kidney failure risk for a hypothetical 57.28-year-old female who is not from North America and has specific clinical characteristics:

```python
from kfre import kfre_person

for years in [2, 5]:
    risk_percentage = (
        kfre_person(
            age=57.28,
            is_male=False,  # is the patient male?
            eGFR=15.0,  # ml/min/1.73 m^2
            uACR=1762.001840,  # mg/g
            is_north_american=False,  # is the patient from North America?
            years=years,
            ####################################################################
            # Uncomment "dm" and "htn" for the 6-variable model:
            ####################################################################
            # dm=0,
            # htn=1,
            ####################################################################
            # Comment out "dm" and "htn" and uncomment the following lines for
            # the 8-variable model:
            ####################################################################
            # albumin=3.0, # g/dL
            # phosphorous=3.162, # mg/dL
            # bicarbonate=21.3, # mEq/L
            # calcium=9.72, # mg/dL
        )
        * 100  # multiply by 100 to convert to percentage
    )

    message = f"The {years}-year risk of kidney failure for this patient is"
    print(f"{message} {risk_percentage:.2f}%.")
```
```
The 2-year risk of kidney failure for this patient is 44.66%.
The 5-year risk of kidney failure for this patient is 89.89%.
```

Ensure to:
- Uncomment `dm` and `htn` if you are using the 6-variable KFRE model.
- For the 8-variable KFRE, keep `dm` and `htn` commented out and instead, uncomment the `albumin`, `phosphorous`, `bicarbonate`, and `calcium` variables.


## Batch Risk Calculation for Multiple Patients
The kfre library provides the functionality to perform batch processing of patient data, allowing for the computation of kidney failure risk predictions across multiple patients in a single operation. This capability is especially valuable for researchers and clinicians needing to assess risks for large cohorts or patient groups.

**Key Features**

When using the `add_kfre_risk_col` function, the library will append new columns for each specified variable model (4-variable, 6-variable, 8-variable) and each time frame (2 years, 5 years) directly to the original DataFrame. This facilitates a seamless integration of risk predictions into existing patient datasets without the need for additional data manipulation steps.

***Disclaimer***

The `kfre` library is designed to facilitate risk prediction using Tangri's KFRE model based on a given set of patient data. It is crucial to ensure that all patient data within a batch calculation are consistent in terms of regional categorization—that is, either all North American or all non-North American. To this end, it is crucial to ensure that all patient data within a batch calculation are consistent in terms of regional categorization. Mixing patient data from different regions within a single batch is not supported, as the function is set to apply one regional coefficient set at a time. This approach ensures the accuracy and reliability of the risk predictions.

Example Usage:

Here is how to perform batch risk calculations for a group of non-North American patients. Note the importance of maintaining consistency in regional data:

***Note***: The following is a mock example using simulated DataFrame structures to illustrate the function usage.

```python
## Note: Ensure that the units for each laboratory value are consistent with
# your model's requirements.

# mock dataframe example
data = pd.DataFrame(
    {
        "Age": [65, 70, 60, 75, 80],
        "Sex": ["male", "female", "female", "male", "female"],
        "eGFR": [19, 50, 45, 22, 30],  # eGFR in mL/min/1.73 m^2
        "uACR": [30, 35, 25, 40, 50],  # uACR in mg/g
        "Diabetes": [1, 0, 0, 1, 1],  # 1 for diabetes, 0 for no diabetes
        "Hypertension": [1, 1, 0, 1, 0],  # 1 for hypertension, 0 for no hypertension
        "Albumin": [3.5, 4.0, 3.8, 3.3, 3.7],  # Serum albumin in g/dL
        "Phosphorus": [3.5, 4.1, 3.9, 4.5, 3.2],  # Serum phosphorus in mg/dL
        "Bicarbonate": [24, 22, 25, 21, 23],  # Serum bicarbonate in mEq/L
        "Calcium": [9.5, 9.7, 9.4, 8.8, 9.6],  # Serum calcium in mg/dL
    }
)

data_with_risks = add_kfre_risk_col(
    df=data,
    age_col="Age",
    sex_col="Sex",
    eGFR_col="eGFR",
    uACR_col="uACR",
    dm_col="Diabetes",
    htn_col="Hypertension",
    albumin_col="Albumin",
    phosphorous_col="Phosphorus",
    bicarbonate_col="Bicarbonate",
    calcium_col="Calcium",
    num_vars=[4, 6, 8],  # can also be a tuple
    years=(2, 5),  # can also be a list
    is_north_american=False,
    copy=True,  # Work on a copy of the DataFrame
)


# The resulting DataFrame 'data' now includes new columns with risk predictions
# for each model and time frame
data_with_risks
```

| **Age** | **Sex** | **eGFR** | **uACR** | **Diabetes** | **Hypertension** | **Albumin** | **Phosphorus** | **Bicarbonate** | **Calcium** | **kfre_4var_2year** | **kfre_4var_5year** | **kfre_6var_2year** | **kfre_6var_5year** | **kfre_8var_2year** | **kfre_8var_5year** |
|---------|:-------:|:--------:|:--------:|:------------:|:----------------:|:-----------:|:--------------:|:---------------:|:-----------:|:-------------------:|:-------------------:|:-------------------:|:-------------------:|:-------------------:|:-------------------:|
| 65      |   male  |    19    |    30    |       1      |         1        |     3.5     |       3.5      |        24       |     9.5     |       0.063123      |       0.223128      |       0.060014      |       0.209336      |       0.069774      |       0.277728      |
| 70      |  female |    50    |    35    |       0      |         1        |      4      |       4.1      |        22       |     9.7     |       0.00155       |       0.005987      |       0.001717      |       0.006501      |       0.00303       |       0.013559      |
| 60      |  female |    45    |    25    |       0      |         0        |     3.8     |       3.9      |        25       |     9.4     |       0.002893      |       0.011156      |       0.002773      |       0.010484      |       0.004705      |       0.020993      |
| 75      |   male  |    22    |    40    |       1      |         1        |     3.3     |       4.5      |        21       |     8.8     |       0.041757      |       0.152247      |       0.039731      |       0.142611      |       0.09375       |       0.357774      |
| 80      |  female |    30    |    50    |       1      |         0        |     3.7     |       3.2      |        23       |     9.6     |       0.013457      |       0.051111      |       0.011059      |       0.041325      |       0.016574      |       0.072424      |


## `add_kfre_risk_col`

Purpose:

This function is designed to compute the risk of chronic kidney disease (CKD) over specified or all possible models and time frames, directly appending the results as new columns to the provided DataFrame. It organizes the results by model (4-variable, 6-variable, 8-variable) first, followed by the time frame (2 years, 5 years) for each model type.

Usage: 

```python
df = add_kfre_risk_col(
    df=df,
    age_col="Age",
    sex_col="SEX",
    eGFR_col="eGFR-EPI",
    uACR_col="uACR",
    dm_col="Diabetes (1=yes; 0=no)",
    htn_col="Hypertension (1=yes; 0=no)",
    albumin_col="Albumin_g_dl",
    phosphorous_col="Phosphate_mg_dl",
    bicarbonate_col="Bicarbonate (mmol/L)",
    calcium_col="Calcium_mg_dl",
    num_vars=8,
    years=(2, 5),
    is_north_american=False,
    copy=False  # Modify the original DataFrame directly
)
```

Parameters: 

- `df` (DataFrame): The patient data containing required clinical parameters.
- `age_col`, `sex_col`, `eGFR_col`, `uACR_col`, `dm_col`, `htn_col`, `albumin_col`, `phosphorous_col`, `bicarbonate_col`, `calcium_col` (str): Column names in df that correspond to the clinical parameters required for risk calculation.
- `num_vars` (int or list): Specifies the number of variables to use for the risk calculations (4, 6, or 8). It determines the complexity of the model applied.
- `years` (tuple, list, or int): Specifies the time frames over which to calculate the risk. Valid inputs include combinations of 2 and 5 years.
- `is_north_american` (bool): Flag indicating whether the patient data should be analyzed with coefficients specific to the North American population.
- `copy` (bool): If set to True, operates on and returns a copy of the DataFrame. If False, modifies the original DataFrame directly.

Returns: 

- `DataFrame`: The modified DataFrame with new columns added for each model and time frame specified. Columns are named following the pattern `pred_{model_var}var_{year}year`, where `{model_var}` is the number of variables (4, 6, or 8) and `{year}` is the time frame (2 or 5).

## Conversion of Clinical Parameters

The `kfre` library includes a utility function `perform_conversions` designed to convert clinical measurement units. This function is especially useful when preparing data for analyses that require specific units. It can handle conversions for multiple parameters, such as urinary protein-creatinine ratio (uPCR), calcium, phosphate, and albumin levels.

**Key Features**

- **Flexible Conversion:** The function supports both standard and reverse conversions, allowing users to switch between units as needed.
- **Batch Processing:** It can process entire columns of data, making it suitable for datasets with multiple patients.
- **Custom Column Names:** Users can specify which columns to convert, providing flexibility in handling datasets with varied naming conventions.

**Parameters**

- `df` (DataFrame): The DataFrame containing the data to be converted.
- `reverse` (bool): If True, performs the reverse conversion (e.g., mmol/L to mg/dL). If False, performs the standard conversion (e.g., mg/dL to mmol/L).
- `convert_all` (bool): If True, attempts to automatically identify and convert all recognized columns.
- `upcr_col`, `calcium_col`, `phosphate_col`, `albumin_col` (str, optional): Column names in the DataFrame that contain the values to be converted.

### Convert Specific Variables from mmol/L to mg/g and/or g/dL

#### uPCR to uACR
The conversion of uPCR from mg/mmol to mg/g involves understanding that both mg/mmol and mg/g are ratios that can be related through their units.

- mg/mmol is a ratio of mass (in milligrams) to molar concentration (in millimoles), while
- mg/g is a ratio of mass (in milligrams) to mass (in grams).

To convert mg/mmol to mg/g, we need to know the molar mass of creatinine, because uPCR is the ratio of the mass of protein to the mass of creatinine. The molar mass of creatinine is approximately 113.12 g/mol. Therefore, 1 mmol of creatinine is 113.12 mg.

Here's the conversion:

1 mg/mmol means that you have 1 mg of protein for every 1 mmol of creatinine. Since 1 mmol of creatinine is 113.12 mg:

$$ \frac{\text{1 mg}}{\text{1 mmol creatinine}} \times \frac{\text{113.12 mg creatinine}}{\text{1 g creatinine}} = 113.12 \text{ mg/g} $$

However, since we are interested in a ratio where the denominator is 1 g (or 1000 mg) rather than 113.12 mg, we use the following calculation:

$$ \frac{\text{1 mg protein}}{\text{0.11312 g creatinine}} \approx 8.84  {\text{ mg/g}} $$

#### Calcium

Calcium is often measured in millimoles per liter (mmol/L) and needs to be converted to milligrams per deciliter (mg/dL) for certain clinical applications or study comparisons.
- Molecular weight of Calcium (Ca): Calcium's atomic weight is approximately 40.08 g/mol.
- Conversion factor: To convert mmol/L to mg/dL for calcium, you multiply by 4. This is derived as follows:

$$ \text{1 mmol/L} \times  \frac{\text{40.08 mg}}{{\text{1 mmol}}} \times \frac{\text {1L} } {\text{10 dL}} = 4.008 \text{ mg/dL}$$

#### Phosphate

Phosphate concentrations are similarly reported in mmol/L but often need to be expressed in mg/dL.

- Molecular weight of Phosphate (PO₄³⁻): The molar mass of phosphate as an ion (considering phosphorus and oxygen) is approximately 94.97 g/mol.
- Conversion factor: To convert mmol/L to mg/dL for phosphate:

$$ \text{1 mmol/L} \times  \frac{\text{94.97 mg}}{{\text{1 mmol}}} \times \frac{\text {1L} } {\text{10 dL}} \approx 9.497 \text{ mg/dL}$$

The clinical conversion factor used is slightly simplified to 3.1, likely a rounded approximation or specific to the binding state of phosphate in clinical assays.

#### Albumin

Albumin measurements are often made in grams per liter (g/L) and converted to grams per deciliter (g/dL) for standard reporting in many clinical contexts.

Conversion factor: Converting g/L to g/dL is straightforward as it involves shifting the decimal point:

$$ 1\text{ g/L} \div 10 = 0.1 \text { g/dL} $$

These conversions help ensure consistency in reporting and interpreting lab values across different systems and studies, facilitating better comparison and understanding of patient data.

**Usage Example**

The following is a mock example to illustrate the usage of the `perform_conversions` function. This example shows how to convert values from mmol to mg for various clinical parameters within a DataFrame.

```python
# Sample DataFrame
df = pd.DataFrame(
    {
        "uPCR (mmol)": [0.5, 0.7, 0.2],  # Example values that need conversion
        "Calcium (mmol)": [2.5, 2.0, 2.2],
        "Phosphate": [1.2, 1.3, 1.1],
        "Albumin": [0.45, 0.50, 0.47],
    }
)

# Perform conversions using the wrapper function, specifying all parameters
# Perform conversions and specify new column names
converted_df = perform_conversions(
    df=df,
    reverse=False,
    upcr_col="uPCR (mmol)",
    calcium_col="Calcium",
    albumin_col="Albumin",
    convert_all=True,
)

# Print the DataFrame to see the changes
converted_df
```
```
Converted 'uPCR (mmol)' to new column 'uPCR_mg_g' with factor 8.84016973125884
Converted 'Calcium (mmol)' to new column 'Calcium_mg_dl' with factor 4
Converted 'Phosphate' to new column 'Phosphate_mg_dl' with factor 3.1
Converted 'Albumin' to new column 'Albumin_g_dl' with factor 0.1
```

| **uPCR   (mmol)** | **Calcium (mmol)** | **Phosphate** | **Albumin** | **uPCR_mg_g** | **Calcium_mg_dl** | **Phosphate_mg_dl** | **Albumin_g_dl** |
|:-----------------:|:------------------:|:-------------:|:-----------:|:-------------:|:-----------------:|:-------------------:|:----------------:|
|        0.5        |         2.5        |      1.2      |     0.45    |    4.420085   |         10        |         3.72        |       0.045      |
|        0.7        |          2         |      1.3      |     0.5     |    6.188119   |         8         |         4.03        |       0.05       |
|        0.2        |         2.2        |      1.1      |     0.47    |    1.768034   |        8.8        |         3.41        |       0.047      |


## Contributor/Maintainer

<img align="left" width="150" height="150" src="https://www.leonshpaner.com/author/leon-shpaner/avatar_hu48de79c369d5f7d4ff8056a297b2c4c5_1681850_270x270_fill_q90_lanczos_center.jpg">

[Leonid Shpaner](https://github.com/lshpaner) is a Data Scientist at UCLA Health. With over a decade experience in analytics and teaching, he has collaborated on a wide variety of projects within financial services, education, personal development, and healthcare. He serves as a course facilitator for Data Analytics and Applied Statistics at Cornell University and is a lecturer of Statistics in Python for the University of San Diego’s M.S. Applied Artificial Intelligence program.

<br><br>

## License
`kfre` is distributed under the MIT License. See [`LICENSE`](LICENSE.md) for more information.

## Support
If you have any questions or issues with `kfre`, please open an issue on this GitHub repository.

## Acknowledgements
The KFRE model developed by Tangri et al. has made significant contributions to kidney disease research.

The `kfre` library is based on the risk prediction models developed in the studies referenced below. Please refer to these studies for an in-depth understanding of the kidney failure risk prediction models used within this library.


## References

1. Tangri N, Grams ME, Levey AS, Coresh J, Appel LJ, Astor BC, Chodick G, Collins AJ, Djurdjev O, Elley CR, Evans M, Garg AX, Hallan SI, Inker LA, Ito S, Jee SH, Kovesdy CP, Kronenberg F, Heerspink HJL, Marks A, Nadkarni GN, Navaneethan SD, Nelson RG, Titze S, Sarnak MJ, Stengel B, Woodward M, Iseki K, for the CKD Prognosis Consortium. (2016). *Multinational assessment of accuracy of equations for predicting risk of kidney failure: A meta-analysis. JAMA,* **315**(2), 164–174. doi: 10.1001/jama.2015.18202.

2. Tangri, N., Stevens, L. A., Griffith, J., Tighiouart, H., Djurdjev, O., Naimark, D., Levin, A., & Levey, A. S. (2011). *A predictive model for progression of chronic kidney disease to kidney failure. JAMA,* **305**(15), 1553-1559. doi: 10.1001/jama.2011.451.  

3. Sumida K, Nadkarni GN, Grams ME, Sang Y, Ballew SH, Coresh J, Matsushita K, Surapaneni A, Brunskill N, Chadban SJ, Chang AR, Cirillo M, Daratha KB, Gansevoort RT, Garg AX, Iacoviello L, Kayama T, Konta T, Kovesdy CP, Lash J, Lee BJ, Major RW, Metzger M, Miura K, Naimark DMJ, Nelson RG, Sawhney S, Stempniewicz N, Tang M, Townsend RR, Traynor JP, Valdivielso JM, Wetzels J, Polkinghorne KR, Heerspink HJL, for the Chronic Kidney Disease Prognosis Consortium. (2020). Conversion of urine protein-creatinine ratio or urine dipstick protein to urine albumin-creatinine ratio for use in chronic kidney disease screening and prognosis. *Ann Intern Med,* ***173***(6), 426-435. doi: 10.7326/M20-0529.


