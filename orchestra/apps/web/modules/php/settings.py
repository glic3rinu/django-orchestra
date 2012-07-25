from django.conf import settings

ugettext = lambda s: s

WEB_PHPVERSION_CHOICES = getattr(settings, 'WEB_PHPVERSION_CHOICES', (
    (None, ugettext('Disabled')),
    ('5', ugettext('PHP5')),
    ('4', ugettext('PHP4')),))

WEB_PHPVERSION_DEFAULT = getattr(settings, 'WEB_PHPVERSION_DEFAULT', 5)
