from django.conf import settings
from django.utils.translation import ugettext_lazy as _

ugettext = lambda s: s

#PERSON = 'P'
#ORGANIZATION = 'O'

CONTACTS_TYPE_CHOICES = getattr(settings, 'CONTACTS_TYPE_CHOICES', (('I', _('Individual')),
                                                                    ('C', _('Company')),
                                                                    ('A', _('Association')),
                                                                    ('P', _('Public_body')),))

CONTACTS_DEFAULT_TYPE = getattr(settings, 'CONTACTS_DEFAULT_TYPE', 'I')

CONTACTS_LANGUAGE_CHOICES = getattr(settings, 'CONTACTS_LANGUAGE_CHOICES', (('ca', ugettext('Catalan')),
                                                          ('es', ugettext('Spanish')),
                                                          ('en', ugettext('English')),))

CONTACTS_DEFAULT_LANGUAGE = getattr(settings, 'CONTACTS_DEFAULT_LANGUAGE', 'en')

CONTACTS_CONTACT_SELF_PK = getattr(settings, 'CONTACTS_CONTACT_SELF_PK', 1)

# Tuple of lowercase models that you don't want to delente when cancel their contract
# Note: the model should not be a dependency of other model, otherwise this doesn't work
CONTACTS_DO_NOT_DELETE_ON_CANCEL = getattr(settings, 'CONTACTS_DO_NOT_DELETE_ON_CANCEL', ('contact'))
