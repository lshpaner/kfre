from setuptools import setup, find_packages

setup(
    name="kfre",
    version="0.1.12",
    author="Leonid Shpaner",
    author_email="lshpaner@ucla.edu",
    description="A Python library for estimating kidney failure risk using the KFRE model developed by Tangri et al.",
    long_description=open("min_readme.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",  # Type of the long description
    package_dir={"": "src"},  # Directory where your package files are located
    # Automatically find packages in the specified directory
    packages=find_packages(where="src"),
    project_urls={  # Optional
        "Author Website": "https://www.leonshpaner.com",
        "Documentation": "https://lshpaner.github.io/kfre/",
        "Zenodo Archive": "https://zenodo.org/records/11100222",
        "Source Code": "https://github.com/lshpaner/kfre",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],  # Classifiers for the package
    python_requires=">=3.7.4",  # Minimum version of Python required
    install_requires=[
        "numpy>=1.18.5",  # Minimum version of numpy required
        "pandas>=1.0.5",  # Minimum version of pandas required
        "matplotlib>=3.2.2",  # Minimum version of matplotlib required
        "seaborn>=0.10.1",  # Minimum version of seaborn required
        "scikit-learn>=0.23.1",  # Minimum version of scikit-learn required
        "tqdm>=4.48.0",  # Minimum version of tqdm required
    ],
)
