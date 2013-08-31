#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
        name='UTH-RHD Code',
        version='0.0.1',
        description='UTH-RHD Project Utility Code',
        author='Dimagi',
        author_email='dev@dimagi.com',
        url='http://www.dimagi.com/',
        packages=find_packages(exclude=['*.pyc']),
        test_suite='sonowatcher.tests',
        test_loader='unittest2:TestLoader',
        install_requires=[
            'requests',
            'python-dateutil',
            'pytz',
            'simplejson',
            'unittest2',
            ],
        )

