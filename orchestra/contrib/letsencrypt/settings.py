from orchestra.contrib.settings import Setting


LETSENCRYPT_AUTO_PATH = Setting('LETSENCRYPT_AUTO_PATH',
    '/home/httpd/letsencrypt/letsencrypt-auto'
)


LETSENCRYPT_LIVE_PATH = Setting('LETSENCRYPT_LIVE_PATH',
    '/etc/letsencrypt/live'
)


LETSENCRYPT_EMAIL = Setting('LETSENCRYPT_EMAIL',
    '',
    help_text="Uses account.email by default",
)
