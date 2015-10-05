def isinstalled(app):
    """ returns True if app is installed """
    from django.conf import settings
    return app in settings.INSTALLED_APPS


def add_app(INSTALLED_APPS, app, prepend=False, append=True):
    """ add app to installed_apps """
    if app not in INSTALLED_APPS:
        if prepend:
            return (app,) + INSTALLED_APPS
        else:
            return INSTALLED_APPS + (app,)
    return INSTALLED_APPS


def remove_app(INSTALLED_APPS, app):
    """ remove app from installed_apps """
    if app in INSTALLED_APPS:
        apps = list(INSTALLED_APPS)
        apps.remove(app)
        return tuple(apps)
    return INSTALLED_APPS
