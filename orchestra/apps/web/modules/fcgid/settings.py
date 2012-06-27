from django.conf import settings

ugettext = lambda s: s

DEFAULT_FCGID_GROUP_PK = getattr(settings, 'DEFAULT_FCGID_GROUP_PK', 1)    
