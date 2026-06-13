"""
adm-lab: Admissibility Laboratory
"""
from setuptools import setup, find_packages

setup(
    name="adm-lab",
    version="0.1.0",
    description="A laboratory for observing admissibility geometry",
    packages=find_packages(exclude=["tests", "experiments"]),
    python_requires=">=3.10",
    extras_require={
        "plot": ["matplotlib>=3.5", "networkx>=2.8"],
    },
)
