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


.. _getting_started:   

Welcome to the KFRE Python Library Documentation!
=============================================================
.. note::
   This documentation is for ``kfre`` stable version ``0.1.16``.


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

- **Python**: version ``3.6`` or higher is required to run ``kfre``.

Additionally, ``kfre`` depends on the following packages, which will be automatically installed when you install ``kfre``:

- **numpy**: version ``1.18.5`` or higher
- **pandas**: version ``1.0.5`` or higher
- **matplotlib**: version ``3.2.2`` or higher
- **seaborn**: version ``0.10.1`` or higher
- **scikit-learn**: version ``0.23.1`` or higher

.. _installation:

Installation
-------------

You can install ``kfre`` directly from PyPI:

.. code-block:: text

    pip install kfre



Table of Contents
====================

.. toctree::
   :maxdepth: 3
   :caption: Getting Started

   getting_started


.. toctree::
   :maxdepth: 3
   :caption: Usage Guide

   usage_guide

.. toctree::
   :maxdepth: 3
   :caption: About KFRE

   validation   
   acknowledgements
   testimonials
   citations
   changelog
   references

   

