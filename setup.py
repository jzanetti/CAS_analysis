#!/usr/bin/env python

""" Setup for cas_analysis"""

from setuptools import find_packages, setup


def main():
    return setup(
        author="Sijin Zhang",
        author_email="zsjzyhzp@gmail.com",
        version="0.0.1",
        description="Crash data analysis",
        maintainer="N/A",
        maintainer_email="N/A",
        name="Sijin Zhang",
        packages=find_packages(),
        zip_safe=False,
    )


if __name__ == "__main__":
    main()