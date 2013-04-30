import os, sys, subprocess, logging
import tempfile
import datetime
from os.path import expanduser

logging.basicConfig(level=logging.DEBUG)

from M2Crypto import X509, ASN1

from pkg_resources import resource_filename

# TODO: refactor this code
# to be CA agnostic and universal, reusable.

def verify(certstring, open_access=False):
    crt = X509.load_cert_string(certstring)

    # Create datetime objects
    now = ASN1.ASN1_UTCTIME()
    now.set_datetime(datetime.datetime.now())
    now = now.get_datetime()
    not_before = crt.get_not_before().get_datetime()
    not_after = crt.get_not_after().get_datetime()

    # Check time.
    if not not_before <= now <= not_after:
       return False
    
    issuer = crt.get_issuer().CN.lower().replace(" ","-")
    logging.debug("Certificate issuer: %s"%(issuer))
    
    # only suport eID certificates
    if issuer not in ("esteid-sk", "esteid-sk-2007", "eid-sk", "eid-sk-2007", "eid-sk-2011", "esteid-sk-2011"):
        return False

    with tempfile.NamedTemporaryFile(prefix="ocsp") as tmp:
        # write the cert to tmp storage
        tmp.write(certstring)
        tmp.flush()
        # construct validation command
        cmdstr = ["openssl", "ocsp", "-nonce",
        "-url", "http://ocsp.sk.ee:80",
        "-issuer", resource_filename(__name__, "certs/%s.pem" %(issuer)),
        "-VAfile", resource_filename(__name__, "certs/sk-ocsp-responder-certificates.pem")]

        if not open_access:
           cmdstr.extend(["-signer", os.path.join(expanduser("~"), '.python-esteid', 'ocsp.pem')])
           cmdstr.extend(["-signkey", os.path.join(expanduser("~"), '.python-esteid', 'ocsp.key')])

        cmdstr.extend(["-cert", tmp.name])	

        logging.debug(" ".join(cmdstr))
        process = subprocess.Popen(cmdstr, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)	
        process.wait()
        (ch_out, ch_err) = (process.stdout.read(), process.stderr.read())

        # TODO: M2Crypto OCSP code
        if ch_err != "Response verify OK\n":
            return False
        logging.debug("Command out: %s\nCommand err:%s" %(ch_out, ch_err))
        if process.returncode == 0:
            if ch_err.startswith("Response verify OK"):
                if ch_out.find("revoked") == -1 and ch_out.find("good") != -1:
                    return True
	return False


if __name__ == "__main__":
	print verify(file(sys.argv[1]).read())
