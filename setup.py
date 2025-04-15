#!/usr/bin/env python
"""
Setup script for the BigBrain Graph RAG project.
"""

from setuptools import setup, find_packages
import os

# Get the long description from the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Package version
VERSION = "0.1.0"

# Core dependencies
INSTALL_REQUIRES = [
    "networkx>=3.0.0",
    "tree-sitter>=0.20.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

# Development and testing dependencies
DEV_REQUIRES = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "flake8>=6.0.0",
    "black>=23.0.0",
]

setup(
    name="bigbrain",
    version=VERSION,
    description="A graph-based RAG system for code understanding",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="BigBrain Team",
    author_email="example@example.com",
    url="https://github.com/example/bigbrain",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="rag graph code-understanding tree-sitter",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.9",
    install_requires=INSTALL_REQUIRES,
    extras_require={
        "dev": DEV_REQUIRES,
    },
    entry_points={
        "console_scripts": [
            "bigbrain=cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "bigbrain": ["grammars/*.so"],
    },
)
