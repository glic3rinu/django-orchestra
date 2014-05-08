from django.conf import settings


# Data access

LISTS_DOMAIN_MODEL = getattr(settings, 'LISTS_DOMAIN_MODEL', 'domains.Domain')

LISTS_DEFAULT_DOMAIN = getattr(settings, 'LIST_DEFAULT_DOMAIN', 'grups.orchestra.lan')
