# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sys
import os

setup(
    name='python-esteid',
    version='0.1.8',
    description='Utilities for Estonian eID and mID infrastructure',
    long_description= open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    classifiers=['Topic :: Utilities',
                 'Topic :: Security :: Cryptography',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 2.5',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: Implementation :: CPython'],
    author='Martin Paljak',
    author_email='martin@martinpaljak.net',
    url='https://github.com/martinpaljak/python-esteid',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=['M2Crypto>=0.22',
                      'python-ldap>=2.4.10',
                      'cliff>=1.3.2'],
    entry_points={'console_scripts': ['sk = esteid.main:main'],
                  'esteid.cli': ['ldap = esteid.cli:LDAP',
                                 'ssh = esteid.cli:SSH',
                                 'verify = esteid.cli:Verify',
                                 'token = esteid.cli:AccessToken']},
    dependency_links=['http://github.com/martinpaljak/M2Crypto/tarball/master#egg=M2Crypto-0.22'],
    )

