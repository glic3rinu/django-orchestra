from django.conf import settings

ugettext = lambda s: s

PHPVERSION_CHOICES = getattr(settings, 'PHPVERSION_CHOICES', (
    (None, ugettext('Disabled')),
    (5, ugettext('PHP5')),
    (4, ugettext('PHP4')),))
    
PHPVERSION_DEFAULT = getattr(settings, 'PHPVERSION_DEFAULT', 5)    
