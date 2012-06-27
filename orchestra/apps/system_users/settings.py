from django.conf import settings

ugettext = lambda s: s


SYSTEM_USER_START_UID = getattr(settings, 'SYSTEM_USER_START_UID', 1001)    
DEFAULT_SYSTEM_USER_PRIMARY_GROUP_PK = getattr(settings, 'DEFAULT_USER_PRIMARY_GROUP_PK', 1)    
DEFAULT_SYSTEM_USER_BASE_HOMEDIR = getattr(settings, 'DEFAULT_SYSTEM_USER_BASE_HOMEDIR', '/home/')    
DEFAULT_SYSTEM_USER_SHELL = getattr(settings, 'DEFAULT_SYSTEM_USER_SHELL', '/bin/false')    
