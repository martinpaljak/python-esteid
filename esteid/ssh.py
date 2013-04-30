from M2Crypto import X509
import sk_ldap
import base64

def pem_cert_to_ssh_line(cert):
    """
    Converts a PEM formatted X509 certificate to a SSH2 public key line 
    usable in authorized_keys file.
    """
    def _encode_ssh(buffer):
        n = len(buffer)
        tmp = "" + chr((n >>24) & 0xff)
        tmp += chr((n >>16) & 0xff)
        tmp += chr((n >>8) & 0xff)
        tmp += chr((n) & 0xff)
        tmp += "\000" # remove length
        tmp += buffer[1:]
        return tmp

    crt = X509.load_cert_string(str(cert))
    rsa = crt.get_pubkey().get_rsa()
    key = "\000\000\000\007ssh-rsa"
    key += _encode_ssh(rsa.e[3:])
    key += _encode_ssh(rsa.n[3:])
 
    return "ssh-rsa %s %s" %(base64.b64encode(key), crt.get_ext('subjectAltName').get_value().split(":")[1] + " " + crt.get_subject().O)



def idcode_to_lines(idcode, nodigi=False):
  lines = []
  try:
    cert = sk_ldap.get_pem_from_ldap(idcode, sk_ldap.AUTH, sk_ldap.IDCARD)
    lines.append(pem_cert_to_ssh_line(cert))
  except:
     pass
  if not nodigi:
     # Digi-ID is optional card, thus don't log errors.
     try:
        cert = sk_ldap.get_pem_from_ldap(idcode, sk_ldap.AUTH, sk_ldap.DIGI)
        lines.append(pem_cert_to_ssh_line(cert))
     except:
        pass
  return lines



def process_file(infile, outfile, nodigi=False):
    for codeline in infile:
        codeline = codeline.strip()
        if codeline.startswith('#') or not len(codeline):
            print >> outfile, codeline
            continue
    lines = idcode_to_lines(codeline, nodigi)
    for line in lines:
      print >> outfile, line


