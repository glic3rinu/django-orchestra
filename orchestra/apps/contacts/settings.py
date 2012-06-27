from django.conf import settings
from django.utils.translation import ugettext_lazy as _

ugettext = lambda s: s

PERSON = getattr(settings, 'PERSON', 'P')

ORGANIZATION = getattr(settings, 'ORGANIZATION', 'O')

TYPE_CHOICES = getattr(settings, 'TYPE_CHOICES', ((PERSON, _('Person')),
                                                  (ORGANIZATION, _('Organization')),))

DEFAULT_TYPE = getattr(settings, 'DEFAULT_TYPE', PERSON)

LANGUAGE_CHOICES = getattr(settings, 'LANGUAGE_CHOICES', (('ca', ugettext('Catalan')),
                                                          ('es', ugettext('Spanish')),
                                                          ('en', ugettext('English')),))

DEFAULT_LANGUAGE = getattr(settings, 'DEFAULT_LANGUAGE', 'en')

CONTACT_SELF_PK = getattr(settings, 'CONTACT_SELF_PK', 1)

# Tuple of lowercase models that you don't want to delente when cancel their contract
# Note: the model should not be a dependency of other model, otherwise this doesn't work
DO_NOT_DELETE_ON_CANCEL = getattr(settings, 'DO_NOT_DELETE_ON_CANCEL', ('contact'))
