# Estonian ID-card "ecosystem" helper

 * [![PyPI version](https://badge.fury.io/py/python-esteid.svg)](http://badge.fury.io/py/python-esteid)
 * [![GitHub version](https://badge.fury.io/gh/martinpaljak%2Fpython-esteid.svg)](http://badge.fury.io/gh/martinpaljak%2Fpython-esteid)

The `sk` utility helps to:
 * query ldap.sk.ee in a meaningful way
 * convert ID codes to SSH keys
 * verify certificates against OCSP

This depends on M2Crypto either being available or being able to build it, ditto for python-ldap.

On Debian and derivatives:

    sudo apt-get install build-essential libssl-dev swig libsasl2-dev libldap-dev python-dev

## Usage
Some samples using the ID code of me (Martin Paljak 38207162722) or Edward Lucas (36205030034, found from [this article](http://news.err.ee/v/economy/35ff0796-2c7c-486f-8547-b9861622c1bb)).

- Query my authentication certificate from LDAP:

    `sk ldap 38207162722`

- Parse the certificate as well:

    `sk ldap 38207162722 | openssl x509 -text -noout`
    
- Get my Digi-ID signing certificate:

    `sk ldap 38207162722 --type sign --digi-id`
    
- If there are several certificates (with newer Mobile-ID), you can get them individually:

    `sk ldap 38207162722 --type sign --mobiil-id --idx 2`

- There's a new type of certificates, [e-residents](https://e-estonia.com/e-residents/about/):

    ```
    $ sk ldap 36205030034
    HINT: 36205030034 is an e-resident. Try again with --resident
    ``` 

- So you can easily separate residents and e-residents:

    `sk ldap 36205030034 --resident --type sign`

- If you use SSH and key based authentication, you can easily give access to certain persons:

   `sk ssh 3820716272 36205030034 >> ~/.ssh/authorized_keys`

## Have fun!

Regards,

  `38207162722`
