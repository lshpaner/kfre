# KFRE: Kidney Failure Risk Estimator

[![PyPI](https://img.shields.io/pypi/v/kfre.svg)](https://pypi.org/project/kfre/)
[![Downloads](https://pepy.tech/badge/kfre)](https://pepy.tech/project/kfre)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/lshpaner/kfre/tree/main?tab=License-1-ov-file)
[![Zenodo](https://zenodo.org/badge/DOI/10.5281/zenodo.11100222.svg)](https://doi.org/10.5281/zenodo.11100222)

<br>

<img src="https://raw.githubusercontent.com/lshpaner/kfre/main/assets/kfre_logo.svg" width="200" style="border: none; outline: none; box-shadow: none;" oncontextmenu="return false;">


`kfre` is a Python library designed to estimate the risk of chronic kidney disease (CKD) progression over two distinct timelines: 2 years and 5 years. Using Tangri's Kidney Failure Risk Equation (KFRE), the library provides tools for healthcare professionals and researchers to predict CKD risk based on patient data. It supports predictions for both males and females and includes specific adjustments for individuals from North American and non-North American regions.

## Prerequisites
Before you install `kfre`, ensure you have the following:

- **Python**: Python 3.6 or higher is required to run `kfre`.

Additionally, kfre has the following package dependencies:

- **NumPy**: Version 1.18.5 or higher
- **Pandas**: Version 1.0.5 or higher


## Installation

You can install `kfre` directly from PyPI:

```bash
pip install kfre
```

## Official Documentation

https://lshpaner.github.io/kfre_docs/