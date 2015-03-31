import os


def get_project_dir():
    """ Return the current project path site/project """
    from django.conf import settings
    settings_file = os.sys.modules[settings.SETTINGS_MODULE].__file__
    return os.path.dirname(os.path.normpath(settings_file))


def get_project_name():
    """ Returns current project name """
    return os.path.basename(get_project_dir())


def get_site_dir():
    """ Returns project site path """
    return os.path.abspath(os.path.join(get_project_dir(), '..'))


def get_orchestra_dir():
    """ Returns orchestra base path """
    import orchestra
    return os.path.dirname(os.path.realpath(orchestra.__file__))
