"""
Setup script for Clinical Trials Data Scraper
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="clinical-trials-scraper",
    version="1.0.0",
    author="Data Scraper Team",
    author_email="",
    description="A Python-based data scraper for retrieving clinical trials information from ClinicalTrials.gov API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "clinical-trials-scraper=main:main",
        ],
    },
    keywords="clinical-trials, data-scraping, medical-research, api, healthcare",
    project_urls={
        "Bug Reports": "",
        "Source": "",
        "Documentation": "",
    },
)
