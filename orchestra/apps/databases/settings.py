from django.conf import settings

ugettext = lambda s: s

DATABASES_DATABASE_TYPE_CHOICES = getattr(settings, 'DATABASES_DATABASE_TYPE_CHOICES', (('mysql', ugettext('MySQL')),
                                                                    ('postgresql', ugettext('PostgreSQL')),))

DATABASES_DEFAULT_DATABASE_TYPE = getattr(settings, 'DATABASES_DEFAULT_DATABASE_TYPE', 'mysql')

DATABASES_DEFAULT_HOST = getattr(settings, 'DATABASES_DEFAULT_HOST', 'web.pangea.lan')

# Data access
DATABASES_DEFAULT_SELECT = getattr(settings, 'DATABASES_DEFAULT_SELECT', True)
DATABASES_DEFAULT_DELETE = getattr(settings, 'DATABASES_DEFAULT_DELETE', True)
DATABASES_DEFAULT_INSERT = getattr(settings, 'DATABASES_DEFAULT_INSERT', True)
DATABASES_DEFAULT_UPDATE = getattr(settings, 'DATABASES_DEFAULT_UPDATE', True)
# Structure access	
DATABASES_DEFAULT_CREATE = getattr(settings, 'DATABASES_DEFAULT_CREATE', True)
DATABASES_DEFAULT_DROP = getattr(settings, 'DATABASES_DEFAULT_DROP', True)
DATABASES_DEFAULT_ALTER = getattr(settings, 'DATABASES_DEFAULT_ALTER', True)
DATABASES_DEFAULT_INDEX = getattr(settings, 'DATABASES_DEFAULT_INDEX', True)
# Other	
DATABASES_DEFAULT_GRANT = getattr(settings, 'DATABASES_DEFAULT_GRANT', False)
DATABASES_DEFAULT_REFER = getattr(settings, 'DATABASES_DEFAULT_REFER', True)
DATABASES_DEFAULT_LOCK = getattr(settings, 'DATABASES_DEFAULT_LOCK', True)
