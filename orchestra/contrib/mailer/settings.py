from orchestra.contrib.settings import Setting


MAILER_DEFERE_SECONDS = Setting('MAILER_DEFERE_SECONDS',
    (300, 600, 60*60, 60*60*24),
)
