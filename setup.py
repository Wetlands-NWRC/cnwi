from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="cnwi",
        version="0.0.0",
        description="CNWI",
        author="Ryan Hamilton",
        author_email="ryan.hamilton@ec.gc.ca",
        packages=find_packages(exclude=("tests", "test.*"), include=("cnwi", "cnwi.*")),
        entry_points={
            "console_scripts": [
                "cnwi = cnwi.cli:cli",
            ],
        },
    )
