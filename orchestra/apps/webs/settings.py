from django.conf import settings
from django.utils.translation import ugettext_lazy as _


WEBS_PORT_CHOICES = getattr(settings, 'WEBS_PORT_CHOICES', (
    (80, 'HTTP'),
    (443, 'HTTPS'),
))

WEBS_DEFAULT_PORT = getattr(settings, 'WEBS_DEFAULT_PORT', 80)

WEBS_DOMAIN_MODEL = getattr(settings, 'WEBS_DOMAIN_MODEL', 'names.Name')

WEBS_DEFAULT_ROOT = getattr(settings, 'WEBS_DEFAULT_ROOT', '/var/www/%(name)s/')

WEBS_DEFAULT_DIRECTIVES = getattr(settings, 'WEBS_DEFAULT_DIRECTIVES', '')

WEBS_TYPE_CHOICES = getattr(settings, 'WEBS_TYPE_CHOICES', (
    ('static', _("Static")),
    ('php4', _("PHP4")),
    ('php5', _("PHP5")),
    ('wsgi', _("uWSGI")),
))

WEBS_DEFAULT_TYPE = getattr(settings, 'WEBS_DEFAULT_TYPE', 'php5')
