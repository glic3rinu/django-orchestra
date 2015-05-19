from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.settings import Setting
from orchestra.settings import ORCHESTRA_BASE_DOMAIN


ACCOUNTS_TYPES = Setting('ACCOUNTS_TYPES',
    (
        ('INDIVIDUAL', _("Individual")),
        ('ASSOCIATION', _("Association")),
        ('CUSTOMER', _("Customer")),
        ('COMPANY', _("Company")),
        ('PUBLICBODY', _("Public body")),
        ('STAFF', _("Staff")),
        ('FRIEND', _("Friend")),
    ),
    validators=[Setting.validate_choices]
)


ACCOUNTS_DEFAULT_TYPE = Setting('ACCOUNTS_DEFAULT_TYPE',
    'INDIVIDUAL', choices=ACCOUNTS_TYPES)


ACCOUNTS_LANGUAGES = Setting('ACCOUNTS_LANGUAGES',
    (
        ('EN', _('English')),
    ),
    validators=[Setting.validate_choices]
)


ACCOUNTS_DEFAULT_LANGUAGE = Setting('ACCOUNTS_DEFAULT_LANGUAGE',
    'EN',
    choices=ACCOUNTS_LANGUAGES
)


ACCOUNTS_SYSTEMUSER_MODEL = Setting('ACCOUNTS_SYSTEMUSER_MODEL',
    'systemusers.SystemUser',
    validators=[Setting.validate_model_label],
)


ACCOUNTS_MAIN_PK = Setting('ACCOUNTS_MAIN_PK',
    1
)


ACCOUNTS_CREATE_RELATED = Setting('ACCOUNTS_CREATE_RELATED',
    (
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
    ),
)


ACCOUNTS_SERVICE_REPORT_TEMPLATE = Setting('ACCOUNTS_SERVICE_REPORT_TEMPLATE',
    'admin/accounts/account/service_report.html'
)
