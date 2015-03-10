def normurlpath(path):
    if not path.startswith('/'):
        path = '/' + path
    path = path.rstrip('/')
    return path.replace('//', '/')
