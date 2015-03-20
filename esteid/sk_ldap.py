#!/usr/bin/env python
import ldap, base64, textwrap

MID = "ESTEID (MOBIIL-ID)"
DIGI = "ESTEID (DIGI-ID)"
IDCARD = "ESTEID"
RESIDENT_DIGI = "ESTEID (DIGI-ID E-RESIDENT)"
RESIDENT_MID = "ESTEID (MOBIIL-ID E-RESIDENT)"

AUTH = "Authentication"
SIGN = "Digital Signature"

_ = lambda x: x # please copypaste from lib/libldap.py

LDAP_SERVER = "ldap://ldap.sk.ee"

class LdapError(Exception):
    pass

def get_pems_from_ldap(idcode, cert_type, chip_type):
    """
    Fetches the certificate(s) of the idcode owner from SK LDAP.
    """
    assert idcode.isdigit() and len(idcode) == 11

    server = ldap.initialize(LDAP_SERVER)
    q = server.search('ou=%s,o=%s,c=EE' % (cert_type, chip_type),
            ldap.SCOPE_SUBTREE,
            'serialNumber=%s' % idcode,
            ['userCertificate;binary'])
    result = server.result(q, timeout=10)
    if result[0] != ldap.RES_SEARCH_RESULT:
        raise LdapError(_("Unexpected result type."))
    if not result[1]:
        raise LdapError(_("No results from LDAP query."))
    if len(result[1][0]) != 2 or not isinstance(result[1][0][1], dict) \
            or not result[1][0][1].has_key('userCertificate;binary') \
            or not result[1][0][1]['userCertificate;binary'] \
            or not isinstance(result[1][0][1]['userCertificate;binary'], list):
        raise LdapError(_("Unexpected result format."))
    return [_get_pem_from_der(x) for x in result[1][0][1]['userCertificate;binary']]

def _get_pem_from_der(der):
    """
    Converts DER certificate to PEM.
    """
    return "\n".join(("-----BEGIN CERTIFICATE-----",
        "\n".join(textwrap.wrap(base64.b64encode(der), 64)),
        "-----END CERTIFICATE-----",))
