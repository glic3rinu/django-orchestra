from django.conf import settings

ugettext = lambda s: s

DATABASE_TYPE_CHOICES = getattr(settings, 'DATABASE_TYPE_CHOICES', (('mysql', ugettext('MySQL')),
                                                                    ('postgresql', ugettext('PostgreSQL')),))

DEFAULT_DATABASE_TYPE = getattr(settings, 'DEFAULT_DATABASE_TYPE', 'mysql')

DEFAULT_HOST = getattr(settings, 'DEFAULT_HOST', 'web.pangea.lan')

# Data access
DEFAULT_SELECT = getattr(settings, 'DEFAULT_SELECT', True)
DEFAULT_DELETE = getattr(settings, 'DEFAULT_DELETE', True)
DEFAULT_INSERT = getattr(settings, 'DEFAULT_INSERT', True)
DEFAULT_UPDATE = getattr(settings, 'DEFAULT_UPDATE', True)
# Structure access	
DEFAULT_CREATE = getattr(settings, 'DEFAULT_CREATE', True)
DEFAULT_DROP = getattr(settings, 'DEFAULT_DROP', True)
DEFAULT_ALTER = getattr(settings, 'DEFAULT_ALTER', True)
DEFAULT_INDEX = getattr(settings, 'DEFAULT_INDEX', True)
# Other	
DEFAULT_GRANT = getattr(settings, 'DEFAULT_GRANT', False)
DEFAULT_REFER = getattr(settings, 'DEFAULT_REFER', True)
DEFAULT_LOCK = getattr(settings, 'DEFAULT_LOCK', True)
