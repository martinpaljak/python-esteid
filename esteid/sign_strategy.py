from __future__ import with_statement

from esteid2.digidocservice2.DigiDocService_suds import AddDataFile

class DocStrategyBase(object):
    def __init__(self, doc, params):
        self.doc = doc
        self.params = (params if params else self._prepare_params())

class SignContentStrategy(DocStrategyBase):
    """
    The optional params for __init__ has to be a dict with the
    following contents:

        "content" : base64.b64encode(doc contents),
        "filename" : os.path.basename(doc),
        "filesize" : os.stat(doc).st_size,
        "mimetype" : doc mimetype,
    """
    def _prepare_params(self):
        """Prepare parameters for self.doc, :returns dict of params:"""
        import mimetypes, os, base64
        mimetype = mimetypes.guess_type(self.doc)[0]
        if not mimetype:
            mimetype = 'application/octet-stream'
        content = None
        with open(self.doc, 'rb') as f:
            content = base64.b64encode(f.read())
        return {
                "content" : content,
                "filename" : os.path.basename(self.doc),
                "filesize" : os.stat(self.doc).st_size,
                "mimetype" : mimetype,
        }

    def add_datafile(self, sesscode):
        return AddDataFile(Sesscode=sesscode,
            FileName=self.params['filename'], MimeType=self.params['mimetype'],
            ContentType='EMBEDDED_BASE64', Size=self.params['filesize'],
            Content=self.params['content'])

    def process_signed_doc(self, ddoc, inject_contents):
        return ddoc

class SignHashStrategy(DocStrategyBase):
    """
    The optional params for __init__ has to be a dict with the
    following contents:

        "sha1hash" : base64.b64encode(SHA1 digest of
        <DataFile ...>base64(doc)\n</DataFile>),
        "filename" : os.path.basename(doc),
        "filesize" : os.stat(doc).st_size,
        "mimetype" : doc mimetype,
    """
    def _prepare_params(self):
        template = """<DataFile ContentType="EMBEDDED_BASE64" Filename="%(filename)s" Id="D0" MimeType="%(mimetype)s" Size="%(filesize)s" xmlns="http://www.sk.ee/DigiDoc/v1.3.0#">%(base64data)s
</DataFile>"""
        import mimetypes, os, hashlib, base64, textwrap
        mimetype = mimetypes.guess_type(self.doc)[0]
        if not mimetype:
            mimetype = 'application/octet-stream'
        base64data = None
        with open(self.doc, 'rb') as f:
            base64data = base64.b64encode(f.read())
        s = hashlib.sha1()
        s.update(textwrap.fill(base64data, 64))
        return {
                "sha1hash" : base64.b64encode(s.digest()),
                "filename" : os.path.basename(self.doc),
                "filesize" : os.stat(self.doc).st_size,
                "mimetype" : mimetype,
        }

    def add_datafile(self, sesscode):
        return AddDataFile(Sesscode=sesscode,
            FileName=self.params['filename'], MimeType=self.params['mimetype'],
            ContentType='HASHCODE', Size=self.params['filesize'],
            DigestType='sha1', DigestValue=self.params['sha1hash'])

    def process_signed_doc(self, ddoc, inject_contents):
        if inject_contents:
            ddoc = _inject_contents(self.doc, ddoc)
        return ddoc

def _inject_contents(doc, ddoc):
    from lxml import etree
    import base64
    root = etree.fromstring(ddoc)
    # TODO: find a way around using the namespace
    df = root.find("{http://www.sk.ee/DigiDoc/v1.3.0#}DataFile")
    if not isinstance(df, etree._Element):
        raise AttributeError("DigiDoc XML doesn't contain DataFile attribute.")
    for marker in ("DigestType", "DigestValue"):
        if marker in df.attrib:
            del df.attrib[marker]
    df.attrib["ContentType"] = "EMBEDDED_BASE64"
    with open(doc, 'rb') as f:
        df.text = base64.b64encode(f.read())
    return etree.tostring(root, xml_declaration=True, encoding="utf-8")
