from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.settings import Setting


MAILER_DEFERE_SECONDS = Setting('MAILER_DEFERE_SECONDS',
    (300, 600, 60*60, 60*60*24),
)


MAILER_MESSAGES_CLEANUP_DAYS = Setting('MAILER_MESSAGES_CLEANUP_DAYS',
    7
)


MAILER_NON_QUEUED_PER_REQUEST_THRESHOLD = Setting('MAILER_NON_QUEUED_PER_REQUEST_THRESHOLD',
    2,
    help_text=_("Number of emails that will be sent immediately before starting to queue them."),
)


MAILER_BULK_MESSAGES = Setting('MAILER_BULK_MESSAGES',
    500,
)
