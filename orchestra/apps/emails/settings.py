from django.conf import settings


EMAILS_VIRTUAL_DOMAIN_MODEL = getattr(settings, 'EMAILS_VIRTUAL_DOMAIN_MODEL', 'names.Name')

EMAILS_DEFAULT_BASE_HOME = getattr(settings, 'EMAILS_DEFAULT_BASE_HOME', '/home')
