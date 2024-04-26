from setuptools import setup, find_packages

setup(
    name="kfre",
    version="0.1.1-alpha4",
    author="Leonid Shpaner",
    author_email="Lshpaner@ucla.edu",
    description="A Python library for kidney failure risk estimation using Tangri's KFRE model",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",  # Type of the long description
    url="https://github.com/lshpaner/kfre",  # URL to the repository or documentation
    package_dir={"": "src"},  # Directory where your package files are located
    # Automatically find packages in the specified directory
    packages=find_packages(where="src"),
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
