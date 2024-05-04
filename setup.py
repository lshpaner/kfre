from setuptools import setup, find_packages

setup(
    name="kfre",
    version="0.1.2_b4",
    author="Leonid Shpaner",
    author_email="Lshpaner@ucla.edu",
    description="A Python library for kidney failure risk estimation using Tangri's KFRE model",
    # long_description=open("README.md").read(),
    long_description=open("min_readme.md").read(),
    long_description_content_type="text/markdown",  # Type of the long description
    package_dir={"": "src"},  # Directory where your package files are located
    # Automatically find packages in the specified directory
    packages=find_packages(where="src"),
    project_urls={  # Optional
        "Author Website": "https://www.leonshpaner.com",
        "Documentation": "https://lshpaner.github.io/kfre_docs/",
        "DOI": "https://zenodo.org/records/11100222",
        "Source Code": "https://github.com/lshpaner/kfre",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],  # Classifiers for the package
    python_requires=">=3.6",  # Minimum version of Python required
    install_requires=[
        "numpy>=1.18.5",  # Example of a required library with a minimum version
        "pandas>=1.0.5",  # Example of another required library with a minimum version
    ],
)
