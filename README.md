# python-esteid

#### Estonian ID-card "ecosystem" helper library and command line utility.

 * [![PyPI version](https://badge.fury.io/py/python-esteid.svg)](http://badge.fury.io/py/python-esteid)
 * [![GitHub version](https://badge.fury.io/gh/martinpaljak%2Fpython-esteid.svg)](http://badge.fury.io/gh/martinpaljak%2Fpython-esteid)

The esteid utility helps to:
 * query ldap.sk.ee in a meaningful way
 * convert ID codes to SSH keys
 * verify certificates against OCSP

Access to the Mobile-ID DigiDocService is currently excluded from the source.

This depends on M2Crypto either being available or being able to build it, ditto for python-ldap.

On Debian and derivatives:

    sudo apt-get install build-essential libssl-dev swig libsasl2-dev libldap-dev python-dev
