from django.conf import settings
from django.utils.translation import ugettext_lazy as _


ACCOUNTS_TYPES = getattr(settings, 'ACCOUNTS_TYPES', (
    ('INDIVIDUAL', _("Individual")),
    ('ASSOCIATION', _("Association")),
    ('CUSTOMER', _("Customer")),
    ('COMPANY', _("Company")),
    ('PUBLICBODY', _("Public body")),
))

ACCOUNTS_DEFAULT_TYPE = getattr(settings, 'ACCOUNTS_DEFAULT_TYPE', 'INDIVIDUAL')


ACCOUNTS_LANGUAGES = getattr(settings, 'ACCOUNTS_LANGUAGES', (
    ('en', _('English')),
))


ACCOUNTS_DEFAULT_LANGUAGE = getattr(settings, 'ACCOUNTS_DEFAULT_LANGUAGE', 'en')


ACCOUNTS_MAIN_PK = getattr(settings, 'ACCOUNTS_MAIN_PK', 1)


ACCOUNTS_CREATE_RELATED = getattr(settings, 'ACCOUNTS_CREATE_RELATED', (
    # <model>, <key field>, <kwargs>, <help_text>
    ('systemusers.SystemUser',
        'username',
        {
            'username': 'account.username',
            'password': 'account.password',
            'is_main': 'True',
        },
        _("Designates whether to creates a related system user with the same username and password or not."),
    ),
    ('mailboxes.Mailbox',
        'name',
        {
            'name': 'account.username',
            'password': 'account.password',
        },
        _("Designates whether to creates a related mailbox with the same name and password or not."),
    ),
    ('domains.Domain',
        'name',
        {
            'name': '"%s.orchestra.lan" % account.username'
        },
        _("Designates whether to creates a related subdomain &lt;username&gt;.orchestra.lan or not."),
    ),
))
