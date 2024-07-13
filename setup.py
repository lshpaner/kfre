from setuptools import setup, find_packages

setup(
    name="kfre",
    version="0.1.8",
    author="Leonid Shpaner",
    author_email="lshpaner@ucla.edu",
    description="A Python library for estimating kidney failure risk using the KFRE model developed by Tangri et al.",
    long_description=open("min_readme.md").read(),
    long_description_content_type="text/markdown",  # Type of the long description
    package_dir={"": "src"},  # Directory where your package files are located
    # Automatically find packages in the specified directory
    packages=find_packages(where="src"),
    project_urls={  # Optional
        "Author Website": "https://www.leonshpaner.com",
        "Documentation": "https://lshpaner.github.io/kfre_docs/",
        "Zenodo Archive": "https://zenodo.org/records/11100222",
        "Source Code": "https://github.com/lshpaner/kfre",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],  # Classifiers for the package
    python_requires=">=3.6",  # Minimum version of Python required
    install_requires=[
        "numpy>=1.18.5",  # Minimum version of numpy required
        "pandas>=1.0.5",  # Minimum version of pandas required
    ],
)
