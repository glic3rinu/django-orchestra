from django.conf import settings

ugettext = lambda s: s


SYSTEM_USERS_START_UID = getattr(settings, 'SYSTEM_USERS_DEFAULT_START_UID', 1001)
SYSTEM_USERS_DEFAULT_PRIMARY_GROUP_PK = getattr(settings, 'SYSTEM_USERS_DEFAULT_PRIMARY_GROUP_PK', 1)
SYSTEM_USERS_DEFAULT_BASE_HOMEDIR = getattr(settings, 'SYSTEM_USERS_DEFAULT_BASE_HOMEDIR', '/home/')
SYSTEM_USERS_DEFAULT_SHELL = getattr(settings, 'SYSTEM_USERS_DEFAULT_SHELL', '/bin/false')
