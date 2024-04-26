# kfre: Kidney Failure Risk Estimator

![PyPI](https://img.shields.io/pypi/v/kfre.svg)

`kfre` is a Python library designed to estimate the risk of chronic kidney disease (CKD) progression over two distinct timelines: 2 years and 5 years. Using Tangri's Kidney Failure Risk Equation (KFRE), the library provides tools for healthcare professionals and researchers to predict CKD risk based on patient data. It supports predictions for both males and females and includes specific adjustments for individuals from North American and non-North American regions.


## Features

- **Risk Prediction**: Utilize Tangri’s validated risk prediction model to estimate kidney failure risk using
    - 4 variables: sex, age, eGFR, uACR (log-normalized)
    - 6 variables: sex, age, eGFR, uACR (log-normalized), diabetes mellitus, hypertension
    - 8 variables: sex, age, eGFR, uACR (log-normalized), serum albumin, serum phosphorous, serum calcium, and serum bicarbonate.
- **Data Flexibility**: Handles various input data formats and maps them to required model parameters.
- **Conversion Utilities**: Includes functions to convert common laboratory results to the required units for risk prediction.

## Important Note on Data Units
The kfre library requires precise data input, with clear specification of the units for each variable. The variables can be expressed in multiple units, and it's crucial that the data being used clearly delineates which units the variables are expressed in. For instance:

- uACR (Urinary Albumin-Creatinine Ratio) can be expressed in either mg/g or mg/mmol.
- Albumin levels can be measured in g/dL or g/L.
- Phosphorous levels can be noted in mg/dL or mmol/L.
- Bicarbonate can be recorded in mEq/L or mmol/L.
- Calcium can be documented in mg/dL or mmol/L.

This flexibility allows the library to be used with a variety of clinical data sources, enhancing its applicability across different healthcare settings.

## Installation

You can install `kfre` directly from PyPI:

```bash
pip install kfre
```

## Documentation
For more details on the API and advanced features, please refer to the full documentation.

## License
kfre is distributed under the MIT License. See `LICENSE` for more information.

## Support
If you have any questions or issues with `kfre`, please open an issue on this GitHub repository.

## Acknowledgements
Tangri's KFRE model and its contributions to kidney disease research.

## References
The `kfre` library is based on the risk prediction models developed in the following studies:

- Tangri, N., Stevens, L. A., Griffith, J., Tighiouart, H., Djurdjev, O., Naimark, D., Levin, A., & Levey, A. S. (2011). A predictive model for progression of chronic kidney disease to kidney failure. JAMA, **305**(15), 1553-1559. doi: 10.1001/jama.2011.451.  

- Tangri N, Grams ME, Levey AS, Coresh J, Appel LJ, Astor BC, Chodick G, Collins AJ, Djurdjev O, Elley CR, Evans M, Garg AX, Hallan SI, Inker LA, Ito S, Jee SH, Kovesdy CP, Kronenberg F, Heerspink HJL, Marks A, Nadkarni GN, Navaneethan SD, Nelson RG, Titze S, Sarnak MJ, Stengel B, Woodward M, Iseki K, for the CKD Prognosis Consortium. (2016). Multinational assessment of accuracy of equations for predicting risk of kidney failure: A meta-analysis. JAMA, **315**(2), 164–174. doi: 10.1001/jama.2015.18202.


Please refer to these studies for an in-depth understanding of the kidney failure risk prediction models used within this library.

