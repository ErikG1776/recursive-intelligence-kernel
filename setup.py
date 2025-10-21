from setuptools import setup, find_packages

setup(
    name="rik-sdk",
    version="0.1.0",
    description="Lightweight Python SDK for the Recursive Intelligence Kernel (RIK) API.",
    author="Erik Galardi",
    packages=find_packages(),
    install_requires=[
        # Core API and SDK dependencies
        "requests>=2.31.0,<3.0.0",
        "fastapi>=0.104.0,<1.0.0",
        "uvicorn>=0.24.0,<1.0.0",
        "pydantic>=2.0.0,<3.0.0",

        # Schema validation and reasoning
        "jsonschema>=4.19.0,<5.0.0",

        # Machine learning and clustering
        "scikit-learn>=1.3.0,<2.0.0",
        "numpy>=1.24.0,<2.0.0",

        # Graph analysis
        "networkx>=3.1,<4.0",

        # Visualization and reporting
        "matplotlib>=3.7.0,<4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "browser": [
            "selenium>=4.10.0",
            "playwright>=1.35.0",
        ],
    },
    python_requires=">=3.8",
)