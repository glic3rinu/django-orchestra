from django.conf import settings

ugettext = lambda s: s

WEB_DEFAULT_FCGID_GROUP_PK = getattr(settings, 'WEB_DEFAULT_FCGID_GROUP_PK', 1)
