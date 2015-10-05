from orchestra import settings


def site(request):
    """ Adds site-related context variables to the context """
    return {
        'ORCHESTRA_SITE_NAME': settings.ORCHESTRA_SITE_NAME,
        'ORCHESTRA_SITE_VERBOSE_NAME': settings.ORCHESTRA_SITE_VERBOSE_NAME
    }
