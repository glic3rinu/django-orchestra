from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from orchestra.settings import ORCHESTRA_BASE_DOMAIN


ACCOUNTS_TYPES = getattr(settings, 'ACCOUNTS_TYPES', (
    ('INDIVIDUAL', _("Individual")),
    ('ASSOCIATION', _("Association")),
    ('CUSTOMER', _("Customer")),
    ('COMPANY', _("Company")),
    ('PUBLICBODY', _("Public body")),
    ('STAFF', _("Staff")),
    ('FRIEND', _("Friend")),
))


ACCOUNTS_DEFAULT_TYPE = getattr(settings, 'ACCOUNTS_DEFAULT_TYPE',
    'INDIVIDUAL'
)


ACCOUNTS_LANGUAGES = getattr(settings, 'ACCOUNTS_LANGUAGES', (
    ('EN', _('English')),
))


ACCOUNTS_SYSTEMUSER_MODEL = getattr(settings, 'ACCOUNTS_SYSTEMUSER_MODEL',
    'systemusers.SystemUser'
)


ACCOUNTS_DEFAULT_LANGUAGE = getattr(settings, 'ACCOUNTS_DEFAULT_LANGUAGE',
    'EN'
)


ACCOUNTS_MAIN_PK = getattr(settings, 'ACCOUNTS_MAIN_PK',
    1
)


ACCOUNTS_CREATE_RELATED = getattr(settings, 'ACCOUNTS_CREATE_RELATED', (
    # <model>, <key field>, <kwargs>, <help_text>
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
            'name': '"%s.{}" % account.username.replace("_", "-")'.format(ORCHESTRA_BASE_DOMAIN),
        },
        _("Designates whether to creates a related subdomain &lt;username&gt;.{} or not.".format(ORCHESTRA_BASE_DOMAIN)),
    ),
))


ACCOUNTS_SERVICE_REPORT_TEMPLATE = getattr(settings, 'ACCOUNTS_SERVICE_REPORT_TEMPLATE',
    'admin/accounts/account/service_report.html'
)
