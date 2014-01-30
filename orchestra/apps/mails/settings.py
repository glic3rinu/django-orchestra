from django.conf import settings


MAILS_VIRTUAL_DOMAIN_MODEL = getattr(settings, 'MAILS_VIRTUAL_DOMAIN_MODEL', 'names.Name')

MAILS_DEFAULT_BASE_HOME = getattr(settings, 'MAILS_DEFAULT_BASE_HOME', '/home')
