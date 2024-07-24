.. _getting_started:   

.. KFRE Python Library Documentation documentation master file, created by
   sphinx-quickstart on Thu May  2 15:44:56 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _target-link:

.. raw:: html

   <div class="no-click">

.. image:: ../assets/kfre_logo.svg
   :alt: KFRE Library Logo
   :align: left
   :width: 200px

.. raw:: html

   </div>

.. raw:: html
   
   <div style="height: 106px;"></div>

\


Welcome to the KFRE Python Library Documentation!
=============================================================
.. important::
   This documentation is for ``kfre`` stable version ``0.1.8``.


``kfre`` is a Python library designed to estimate the risk of chronic kidney disease 
(CKD) progression using the Kidney Failure Risk Equation (KFRE) developed by
Tangri et al. It provides risk assessments over two distinct timelines: 
2 years and 5 years. The library is tailored for healthcare professionals and 
researchers, enabling precise CKD risk predictions based on patient data. 
It supports predictions for both males and females and includes adjustments 
for individuals from North American and non-North American regions.


  

.. **Table of Contents**
.. ---------------------
.. 1. :ref:`Prerequisites <prerequisites>`
.. 2. :ref:`Installation <installation>`
.. 3. :ref:`Usage Guide <usage_guide>`
..     - :ref:`uPCR to uACR <upcr_to_uacr>`
..     - :ref:`Single Patient Risk Calculation <single_patient_risk_calculation>`
..     - :ref:`Batch Risk Calculation <batch_risk_calculation>`
..     - :ref:`Conversion of Clinical Parameters <conversion_clinical_parameters>`
.. 4. :ref:`Contributor/Maintainer <contributor_maintainer>`
.. 5. :ref:`License <license>`
.. 6. :ref:`Support <support>`
.. 7. :ref:`References <references>`



.. _prerequisites:   

Prerequisites
-------------
Before you install ``kfre``, ensure your system meets the following requirements:

- **Python**: Version ``3.6`` or higher is required to run ``kfre``.

Additionally, ``kfre`` depends on the following packages, which will be automatically installed when you install ``kfre`` using pip:

- **numpy**: Version ``1.18.5`` or higher
- **pandas**: Version ``1.0.5`` or higher
- **matplotlib**: Version ``3.2.2`` or higher
- **seaborn**: Version ``0.10.1`` or higher
- **scikit-learn**: Version ``0.23.1`` or higher

.. _installation:

Installation
-------------

You can install ``kfre`` directly from PyPI:

.. code-block:: bash

    pip install kfre


