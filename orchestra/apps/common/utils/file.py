import tarfile 
import cStringIO as StringIO
import time 
import ho.pisa as pisa
import os, cgi


def list_files(paths):
    files = []
    for path in paths:
        for _file in os.listdir(path):
            #exclude hidden files
            if not _file[0] is '.':
                files.append((path+_file, _file))
    return files


def generate_tar_stringio(files, mode=''):
    """ files should be a list of dicts like [{'filename': 'filename', 'file': cStringIO },]"""

    temp_file = StringIO.StringIO()
    tar = tarfile.open(fileobj=temp_file, mode="w:%s" % mode)
    mtime = time.time()
    for f in files:
        file = f['file']
        info = tarfile.TarInfo(f['filename'])
        #Seek to the EOF in order to know th    e size of the file with tell, a bit triky uhu?
        file.seek(0,2)
        info.size = file.tell()
        info.mtime = mtime 
        info.type = tarfile.REGTYPE
        #Go back to the begining
        file.seek(0)
        tar.addfile(tarinfo=info, fileobj=file) 
    tar.close()
    return temp_file.getvalue()


def generate_pdf_stringio(html):
    """ Convert html input to pdf format """
    
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(
        html.encode("UTF-8")), result)
    if not pdf.err:
        return result
    return None
