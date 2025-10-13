from setuptools import setup, find_packages

setup(
    name="rik-sdk",
    version="0.1.0",
    description="Lightweight Python SDK for the Recursive Intelligence Kernel (RIK) API.",
    author="Erik Galardi",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
    ],
    python_requires=">=3.8",
)