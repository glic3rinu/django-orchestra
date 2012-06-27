from django.conf import settings

ugettext = lambda s: s


DEFAULT_INITIAL_STATUS = getattr(settings, 'DEFAULT_INITIAL_STATUS', settings.WAITTING_PROCESSING)
