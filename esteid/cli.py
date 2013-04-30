from cliff.command import Command
import argparse
from esteid import sk_ldap
from esteid import sk_ocsp
from esteid import ssh
import sys

class LDAP(Command):
   """Interface to ldap.sk.ee"""
   
   def get_parser(self, prog_name):
     parser = super(LDAP, self).get_parser(prog_name)
     parser.add_argument('idcode', nargs='+')
     parser.add_argument('--type', dest='cert_type', choices=["auth", "sign"], default="auth")
     parser.add_argument('--digi-id', action='store_true')
     parser.add_argument('--mobiil-id', action='store_true')
     return parser
                            
   
   def take_action(self, parsed_args):
     if parsed_args.digi_id:
       chip_type = sk_ldap.DIGI
     elif parsed_args.mobiil_id:
       chip_type = sk_ldap.MID
     else:
       chip_type = sk_ldap.IDCARD
     
     if parsed_args.cert_type == "auth":
       cert_type = sk_ldap.AUTH
     elif parsed_args.cert_type == "sign":
       cert_type = sk_ldap.SIGN
     
     for idcode in parsed_args.idcode:
       try:
         print sk_ldap.get_pem_from_ldap(idcode, cert_type, chip_type)
       except sk_ldap.LdapError, e:
         print "ERROR for %s" %(idcode)



class SSH(Command):
   """Converts information from ldap.sk.ee to a usable ~/.ssh/authorized_keys file"""
   def get_parser(self, prog_name):
     parser = super(SSH, self).get_parser(prog_name)
     parser.add_argument('--infile', nargs='?', type=argparse.FileType('r'), help='file to read codes from')
     parser.add_argument('--outfile', nargs='?', type=argparse.FileType('w'), help='file to write authorized_keys entries')
     parser.add_argument('idcode', nargs='*')
     parser.add_argument('--no-digi-id', action='store_true', help='don\'t write Digi-ID keys')
     return parser
                                 
   def take_action(self, parsed_args):
     if parsed_args.infile:
       return ssh.process_file(parsed_args.infile, sys.stdout, parsed_args.no_digi_id)
     for idcode in parsed_args.idcode:
       for l in ssh.idcode_to_lines(idcode, parsed_args.no_digi_id):
         print l



class Verify(Command):
   """Verifies certificates (OCSP)"""
   def get_parser(self, prog_name):
     parser = super(Verify, self).get_parser(prog_name)
     parser.add_argument('infile', nargs='+', type=argparse.FileType('r'))
     return parser
   
   def take_action(self, parsed_args):
     for f in parsed_args.infile:
       pem = f.read()
       print "%s: %s" %(f.name, "OK" if sk_ocsp.verify(pem) else  "NOT OK") 
       f.close()
       
     

class AccessToken(Command):
   """Installs the PKCS#12 access token for www.sk.ee services"""
   def get_parser(self, prog_name):
     parser = super(AccessToken, self).get_parser(prog_name)
     parser.add_argument('filename', nargs=1)
     return parser

   def take_action(self, parsed_args):
     print parsed_args.filename
