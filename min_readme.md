<img src="https://raw.githubusercontent.com/lshpaner/kfre/main/assets/kfre_logo.svg" width="200" style="border: none; outline: none; box-shadow: none;" oncontextmenu="return false;">

<br>

[![PyPI](https://img.shields.io/pypi/v/kfre.svg)](https://pypi.org/project/kfre/)
[![Downloads](https://pepy.tech/badge/kfre)](https://pepy.tech/project/kfre)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/lshpaner/kfre/tree/main?tab=License-1-ov-file)
[![Zenodo](https://zenodo.org/badge/DOI/10.5281/zenodo.11100222.svg)](https://doi.org/10.5281/zenodo.11100222)

`kfre` is a Python library designed to estimate the risk of chronic kidney disease (CKD) progression using the Kidney Failure Risk Equation (KFRE) developed by Tangri et al. It provides risk assessments over two distinct timelines: 2 years and 5 years. The library is tailored for healthcare professionals and researchers, enabling precise CKD risk predictions based on patient data. It supports predictions for both males and females and includes adjustments for individuals from North American and non-North American regions.

## Prerequisites
Before you install `kfre`, ensure you have the following:

- **Python**: Python 3.7.4 or higher is required to run `kfre`.

Additionally, kfre has the following package dependencies:

- **numpy**: version 1.18.5 or higher
- **pandas**: version 1.0.5 or higher
- **matplotlib**: version 3.2.2 or higher
- **seaborn**: version 0.10.1 or higher
- **scikit-learn**: version 0.23.1 or higher
- **tqdm**: version 4.48.0 or higher


## Installation

You can install `kfre` directly from PyPI:

```bash
pip install kfre
```

## 📄 Official Documentation

https://lshpaner.github.io/kfre

## 🌐 Author Website

https://www.leonshpaner.com

## ⚖️ License

`kfre` is distributed under the MIT License. See [LICENSE](https://github.com/lshpaner/kfre/blob/main/LICENSE.md) for more information.

## 📚 Citing `kfre`

If you use `kfre` in your research or projects, please consider citing it.

```bibtex
    @software{shpaner_2024_11100222,
      author       = {Shpaner, Leonid},
      title        = {{kfre: A Python Library for Reproducing Kidney 
                       Failure Risk Equations (KFRE)}},
      month        = may,
      year         = 2024,
      publisher    = {Zenodo},
      version      = {0.1.13},
      doi          = {10.5281/zenodo.11100222},
      url          = {https://doi.org/10.5281/zenodo.11100222}
    }
```

## Support
If you have any questions or issues with `kfre`, please open an issue on this GitHub repository.

## Acknowledgements
The KFRE model developed by Tangri et al. has made significant contributions to kidney disease research.

The `kfre` library is based on the risk prediction models developed in the studies referenced below. Please refer to these studies for an in-depth understanding of the kidney failure risk prediction models used within this library.

Special thanks to Panayiotis Petousis, PhD, Obidiugwu Duru, MD, MS, Kenn B. Daratha, PhD, Keith C. Norris, MD, PhD, Katherine R. Tuttle MD, FASN, FACP, FNKF, Susanne B. Nicholas, MD, MPH, PhD, and Alex Bui, PhD. Their exceptional work on end-stage kidney disease has greatly inspired the creation of this library.


References
===========

1. Ali, I., Donne, R. L., & Kalra, P. A. (2021). A validation study of the kidney failure risk equation in advanced chronic kidney disease according to disease aetiology with evaluation of discrimination, calibration and clinical utility. *BMC Nephrology, 22(1),* 194. https://doi.org/10.1186/s12882-021-02402-1 [1]_

2. Kang, M. W. (2024). [KFRE validation dataset, Asian cohort]. Unpublished dataset provided by personal communication, June 26, 2024. Department of Internal Medicine, Seoul National University College of Medicine, Seoul, Korea.

3. Kang, M. W., Tangri, N., Kim, Y. C., An, J. N., Lee, J., Li, L., Oh, Y. K., Kim, D. K., Joo, K. W., Kim, Y. S., Lim, C. S., & Lee, J. P. (2020). An independent validation of the kidney failure risk equation in an Asian population. *Scientific Reports, 10,* 12920. https://doi.org/10.1038/s41598-020-69715-3

4. Sumida, K., Nadkarni, G. N., Grams, M. E., Sang, Y., Ballew, S. H., Coresh, J., Matsushita, K., Surapaneni, A., Brunskill, N., Chadban, S. J., Chang, A. R., Cirillo, M., Daratha, K. B., Gansevoort, R. T., Garg, A. X., Iacoviello, L., Kayama, T., Konta, T., Kovesdy, C. P., Lash, J., Lee, B. J., Major, R. W., Metzger, M., Miura, K., Naimark, D. M. J., Nelson, R. G., Sawhney, S., Stempniewicz, N., Tang, M., Townsend, R. R., Traynor, J. P., Valdivielso, J. M., Wetzels, J., Polkinghorne, K. R., & Heerspink, H. J. L. (2020). Conversion of urine protein-creatinine ratio or urine dipstick protein to urine albumin-creatinine ratio for use in chronic kidney disease screening and prognosis. *Annals of Internal Medicine, 173* (6), 426-435. https://doi.org/10.7326/M20-0529

5. Tangri, N., Grams, M. E., Levey, A. S., Coresh, J., Appel, L. J., Astor, B. C., Chodick, G., Collins, A. J., Djurdjev, O., Elley, C. R., Evans, M., Garg, A. X., Hallan, S. I., Inker, L. A., Ito, S., Jee, S. H., Kovesdy, C. P., Kronenberg, F., Heerspink, H. J. L., Marks, A., Nadkarni, G. N., Navaneethan, S. D., Nelson, R. G., Titze, S., Sarnak, M. J., Stengel, B., Woodward, M., Iseki, K., & for the CKD Prognosis Consortium. (2016). Multinational assessment of accuracy of equations for predicting risk of kidney failure: A meta-analysis. *JAMA, 315* (2), 164–174. https://doi.org/10.1001/jama.2015.18202

6. Tangri, N., Stevens, L. A., Griffith, J., Tighiouart, H., Djurdjev, O., Naimark, D., Levin, A., & Levey, A. S. (2011). A predictive model for progression of chronic kidney disease to kidney failure. *JAMA, 305* (15), 1553-1559. https://doi.org/10.1001/jama.2011.451


.. [1] This article is licensed under a Creative Commons Attribution 4.0 International License. To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/. The Creative Commons Public Domain Dedication waiver (http://creativecommons.org/publicdomain/zero/1.0/) applies to the data made available in this article, unless otherwise stated.


