from django.http import HttpResponse
from common.utils.file import generate_tar_stringio


def download(file, mimetype, filename):
    response = HttpResponse(file, mimetype=mimetype)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    response['Content-Length'] = len(file)
    return response


def download_content(content, content_type, filename):
    """
    Send a content (file) through Django without creating the file into disk.
    StringIO, implements a file-like class that reads and writes a string buffer
    (also known as memory files).
    """
    
    file = StringIO.StringIO(content.encode("UTF-8")).getvalue()
    return download(file, content_type, filename)


def download_files(files, mimetype=''):
    """ files should be a list of dicts like [{'filename': 'filename', 'file': cStringIO },]"""
    
    if len(files) == 0: return
    elif len(files) == 1:
        filename = files[0]['filename']
        mimetype = mimetype
        file = files[0]['file'].getvalue()
    else:
        filename = "transactions.tar.gz"
        mimetype = "application/x-tar-gz"
        file = generate_tar_stringio(files, mode='gz')
        
    return download(file, mimetype, filename)
