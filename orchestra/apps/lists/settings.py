from django.conf import settings


# Data access

LISTS_DOMAIN_MODEL = getattr(settings, 'LISTS_DOMAIN_MODEL', 'emails.Domain')
