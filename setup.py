# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Setup script for py_utils
# ---------------------------------------------------------
# ./setup.py

from setuptools import setup, find_packages

setup(
    name='txt2latex',
    version='0.1.0',
    description='Different helper class and module',
    author='DERAINS Thibaut',
    author_email='thibaut.derains@gmail.com',
    py_modules=['ConfigHelper','Logueur'],
    packages=find_packages(),
    install_requires=[]
)