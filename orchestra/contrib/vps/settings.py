from django.conf import settings


VPS_TYPES = getattr(settings, 'VPS_TYPES', (
    ('openvz', 'OpenVZ container'),
))


VPS_DEFAULT_TYPE = getattr(settings, 'VPS_DEFAULT_TYPE',
    'openvz'
)


VPS_TEMPLATES = getattr(settings, 'VPS_TEMPLATES', (
    ('debian7', 'Debian 7 - Wheezy'),
))


VPS_DEFAULT_TEMPLATE = getattr(settings, 'VPS_DEFAULT_TEMPLATE',
    'debian7'
)
