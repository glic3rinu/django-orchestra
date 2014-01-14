from django.conf import settings


EMAILS_VIRTUAL_DOMAIN_MODEL = getattr(settings, 'EMAILS_VIRTUAL_DOMAIN_MODEL', '/home/')
