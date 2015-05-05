from orchestra.contrib.settings import Setting


MAILER_DEFERE_SECONDS = Setting('MAILER_DEFERE_SECONDS',
    (300, 600, 60*60, 60*60*24),
)


MAILER_MESSAGES_CLEANUP_DAYS = Setting('MAILER_MESSAGES_CLEANUP_DAYS',
    10
)
