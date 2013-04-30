from setuptools import setup, find_packages
import sys, os

version = '0.1.4'

setup(name='python-esteid',
      version=version,
      description="Utilities for Estonian eID and mID infrastructure",
      long_description="""\
""",
      classifiers=['Topic :: Utilities', 'Topic :: Security :: Cryptography'],
      author='Martin Paljak',
      author_email='martin@martinpaljak.net',
      url='https://github.com/martinpaljak/python-esteid',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'suds>=0.4',
          'M2Crypto>=0.21.1',
          'python-ldap>=2.4.10',
          'cliff>=1.3.2'
      ],
      entry_points = {
        'nose.plugins': [
            'mid_token_plugin = tokenplugin:MidTokenPlugin'
        ],
        'console_scripts': [
          'esteid = esteid.main:main'
        ],
        'esteid.cli': [
          'ldap = esteid.cli:LDAP',
          'ssh = esteid.cli:SSH',
          'verify = esteid.cli:Verify',
          'token = esteid.cli:AccessToken',
        ],
       },
      )
