import binascii, textwrap, base64

def cert_to_pem(cert):
    return "\n".join(("-----BEGIN CERTIFICATE-----",
    "\n".join(textwrap.wrap(base64.b64encode(binascii.unhexlify(cert)), 64)),
    "-----END CERTIFICATE-----",))

def str_to_unicode(s):
    """
    Attempts to convert the input string to unicode.
    Only useful for the specific case of extracting names from EstEID
    certifcates.
    """
    try:
        ret = unicode(s, 'utf-16-be')
    except:
        ret = unicode(s, 'utf-8') # can throw
    if any([ ord(c) & (2 << 12) for c in ret ]):
        ret = unicode(s, 'utf-8') # can throw
    return ret
