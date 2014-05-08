from orchestra import settings


def site(request):
    """ Adds site-related context variables to the context """
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_VERBOSE_NAME': settings.SITE_VERBOSE_NAME
    }

