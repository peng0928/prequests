#!python
# -*- coding:utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="requestXpath",
    version='0.1.1.4',
    author="penr",
    author_email="1944542244@qq.com",
    description="Inherit the requests module, add xpath functionality to expand the API, and handle request failures and retries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/peng0928/prequests",
    packages=find_packages(),
    install_requires=["requests", "urllib3", "lxml"],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
