import os


def get_project_root():
    """ Return the current project path site/project """
    from django.conf import settings
    settings_file = os.sys.modules[settings.SETTINGS_MODULE].__file__
    return os.path.dirname(os.path.normpath(settings_file))


def get_project_name():
    """ Returns current project name """
    return os.path.basename(get_project_root())


def get_site_root():
    """ Returns project site path """
    return os.path.abspath(os.path.join(get_project_root(), '..'))


def get_orchestra_root():
    """ Returns orchestra base path """
    import orchestra
    return os.path.dirname(os.path.realpath(orchestra.__file__))
