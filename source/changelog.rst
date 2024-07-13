.. _changelog:   

.. image:: /_static/kfre_logo.svg
   :alt: KFRE Library Logo
   :align: left
   :width: 200px

.. raw:: html

   <div style="height: 106px;"></div>


Changelog
=========

0.1.7
-----

This release includes the following updates and improvements:

- Acknowledgements for key influencers whose exceptional work on end-stage kidney disease has greatly inspired the creation of this library.  

- Implemented comprehensive exception handling within the ``kfre_person()`` function to ensure proper parameter validation:
  - Combined all exceptions into a single exception.
  - Concatenated exceptions using a newline character for better readability.
  - Added checks to ensure ``age``, ``is_male``, ``eGFR``, and ``uACR`` parameters are supplied.
  - Validated that the ``years`` parameter can only be 2 or 5.
  - Ensured ``dm`` and ``htn`` parameters, if provided, are either ``0``, ``1``, ``True``, or ``False``.
  - Added a check to ensure ``is_north_american`` is specified as either ``True`` or ``False``.


0.1.6
-----

This release includes the following updates and improvements:

- Added version information to the ``__init__.py`` file. The version of this release is ``0.1.6``.


0.1.5
-----

This stable release, ``kfre 0.1.5``, builds directly upon the foundations set in version ``0.1.2`` and ``0.1.4`` with no changes to the codebase. The key highlight of this update is a an update of citing version 0.1.5 under citations section on PyPI landing page.

0.1.4
-----

**Documentation Enhancements**

**Core Documentation Migration:** All essential documentation has been transferred to this new site, available here at `lshpaner.github.io/kfre_docs <https://lshpaner.github.io/kfre_docs>`_. This migration enhances accessibility and ease of navigation.

**Visual Updates:** A new logo has been introduced, now featured on both the documentation site and the PyPI landing page to enhance brand recognition.

**Citation Instructions:** Detailed guidance on how to properly cite the kfre project has been added, including a direct link to the Zenodo archive for easy reference.

**Updated References:** All references have been meticulously updated to conform with the latest APA 7 standards.

.. note::

   Why no version ``0.1.3``? In alignment with common superstitions, version ``0.1.3`` was skipped, much like how many buildings lack a 13th floor.

0.1.2
-----

This release, ``kfre 0.1.2``, marks a substantial update from the preliminary alpha versions, introducing significant enhancements and features that elevate the tool's flexibility, accuracy, and ease of use:

**Enhanced Core Functionality:** A comprehensive overhaul from earlier minimal viable products to a more robust and feature-rich application.

New Calculator Function: The introduction of the ``kfre_person()`` function enables risk metrics calculations for individuals one at a time, customizing the analysis to each unique dataset.

**Increased Flexibility:** The ``add_kfre_risk_col()`` function now allows for direct execution of kfre without the need to instantiate a class, simplifying the process for users.

**Model Variability:** Users can specify models with 4, 6, or 8 variables through the ``add_kfre_risk_col()`` function, adapting to different data requirements.

**Timeframe Options:** The function now accommodates specification of projection years (2 or 5 years, or either), providing tailored risk assessments.

**DataFrame Handling:** An option to either copy the dataframe or modify it in place when adding kfre columns is now available, offering greater flexibility in data management.

**Formula Correction:** The formula for the 6-variable calculation has been updated with the correct coefficients from Tangri et al., enhancing prediction accuracy.

**Conversion Tools:** The new `perform_conversions()`` function facilitates the conversion of relevant clinical metrics, streamlining data preparation for analysis.

This release reflects ongoing efforts to enhance and refine `kfre`, driven by feedback from users and continuous research into improving its utility and functionality.



.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Getting Started

   getting_started


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
   references