#!python
# -*- coding:utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages
from requestXpath import requestXpath

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="requestXpath",
    version='0.1.5',
    author="penr",
    author_email="1944542244@qq.com",
    description="继承requests,增加xpath功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/peng0928/prequests",
    packages=find_packages(),
    install_requires=[
        ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
