from django.conf import settings


WEBS_IP_CHOICES = getattr(settings, 'WEBS_IP_CHOICES', (
    ('localhost', '127.0.0.1'),
    ('all', None),
))

WEBS_PORT_CHOICES = getattr(settings, 'WEBS_PORT_CHOICES', (
    ('HTTP', 80),
    ('HTTPS', 443),
))

WEBS_DEFAULT_PORT = getattr(settings, 'WEBS_DEFAULT_PORT', 80)

WEBS_DOMAIN_MODEL = getattr(settings, 'WEBS_DOMAIN_MODEL', 'names.Name')

WEBS_DEFAULT_ROOT = getattr(settings, 'WEBS_DEFAULT_ROOT', '/var/www/%(name)s/')

WEBS_DEFAULT_DIRECTIVES = getattr(settings, 'WEBS_DEFAULT_DIRECTIVES', '')

