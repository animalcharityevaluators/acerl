#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()


setup(
    name='researchlibrary',
    version='0.0.1',
    description='ACE Research Library',
    long_description=README,
    author='Denis Drescher',
    author_email='drescher@claviger.net',
    include_package_data=True,
    url='https://github.com/FUB-HCC/ACE-Research-Library',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    install_requires=[
        'django-jinja',
        'django-flat-theme',
        'django_compressor',
        'Django',
        'psycopg2',
        'pytz',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': []
    }
)
