#!/bin/bash

pkcs12file=${1}
echo -n "Password: "
read password

# read the certificate
openssl pkcs12 -in ${pkcs12file} -passin pass:${password} -nokeys -clcerts | openssl x509 -out ocsp.pem
# read the key
openssl pkcs12 -in ${pkcs12file} -passin pass:${password} -nodes -nocerts | openssl rsa -check -out ocsp.key
