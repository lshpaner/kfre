.. _getting_started:   

.. KFRE Python Library Documentation documentation master file, created by
   sphinx-quickstart on Thu May  2 15:44:56 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _target-link:
.. image:: /_static/kfre_logo.svg
   :alt: KFRE Library Logo
   :align: left
   :width: 200px

.. raw:: html

   <div style="height: 106px;"></div>


Welcome to the KFRE Python Library Documentation!
=============================================================
.. important::
   This documentation is for ``kfre`` stable version ``0.1.7``.


``kfre`` is a Python library designed to estimate the risk of chronic kidney disease 
(CKD) progression using the Kidney Failure Risk Equation (KFRE) developed by
Tangri et al. It provides risk assessments over two distinct timelines: 
2 years and 5 years. The library is tailored for healthcare professionals and 
researchers, enabling precise CKD risk predictions based on patient data. 
It supports predictions for both males and females and includes adjustments 
for individuals from North American and non-North American regions.


.. _prerequisites:   

Prerequisites
-------------
Before you install ``kfre``, ensure your system meets the following requirements:

- **Python**: Version ``3.6`` or higher is required to run ``kfre``.

Additionally, ``kfre`` depends on the following packages, which will be automatically installed when you install ``kfre`` using pip:

- **NumPy**: Version ``1.18.5`` or higher
- **Pandas**: Version ``1.0.5`` or higher


.. _installation:

Installation
-------------

You can install ``kfre`` directly from PyPI:

.. code-block:: bash

    pip install kfre


.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Usage Guide

   usage_guide

.. toctree::
   :hidden:
   :maxdepth: 3
   :caption: About KFRE

   acknowledgements
   citations
   changelog
   references
