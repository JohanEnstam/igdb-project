#!/usr/bin/env python3
"""
Setup configuration for IGDB Game Recommendation System

This setup.py defines the project structure and dependencies for both
development and production environments.
"""

from setuptools import setup, find_packages

# Read requirements from requirements-dev.txt
with open("requirements-dev.txt", "r") as f:
    requirements = []
    dev_requirements = []
    in_dev_section = False

    for line in f:
        line = line.strip()
        if line.startswith("# Development dependencies"):
            in_dev_section = True
            continue
        elif line.startswith("# ") and not line.startswith("# Development"):
            in_dev_section = False
            continue
        elif line and not line.startswith("#"):
            if in_dev_section:
                dev_requirements.append(line)
            else:
                requirements.append(line)

# Core dependencies (production)
core_requirements = [
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    "pandas>=2.1.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "pydantic>=2.5.0",
]

setup(
    name="igdb-recommendation-system",
    version="0.1.0",
    description=(
        "IGDB Game Recommendation System - Complete pipeline for collecting "
        "game data, training ML models, and serving recommendations"
    ),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Johan Enstam",
    author_email="johan@example.com",  # Update with your email
    url="https://github.com/johanenstam/igdb-project",
    packages=find_packages(exclude=["tests*", "docs*", "infrastructure*", "venv*"]),
    python_requires=">=3.11",
    install_requires=core_requirements,
    extras_require={
        "dev": [
            "pre-commit>=3.6.0",
            "black>=23.12.1",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "bandit>=1.7.5",
            "types-requests>=2.31.0",
            "types-PyYAML>=6.0.12",
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=2.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "igdb-ingest=data_pipeline.ingestion.main:main",
            "igdb-process=data_pipeline.processing.main:main",
            "igdb-train=data_pipeline.training.main:main",
            "igdb-serve=web_app.api.main:main",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="igdb games recommendation machine-learning api",
    project_urls={
        "Bug Reports": "https://github.com/johanenstam/igdb-project/issues",
        "Source": "https://github.com/johanenstam/igdb-project",
        "Documentation": "https://github.com/johanenstam/igdb-project/tree/main/docs",
    },
)
