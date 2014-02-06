from django.conf import settings


MAILS_VIRTUAL_DOMAIN_MODEL = getattr(settings, 'MAILS_VIRTUAL_DOMAIN_MODEL', 'names.Domain')

MAILS_DEFAULT_BASE_HOME = getattr(settings, 'MAILS_DEFAULT_BASE_HOME', '/var/vmail')

MAILS_VIRTUAL_MAILBOX = getattr(settings, 'MAILS_VIRTUAL_DOMAIN_MODEL', 'mails.Mailbox')
MAILS_VIRTUAL_MAILDOMAIN = getattr(settings, 'MAILS_VIRTUAL_DOMAIN_MODEL', 'mails.MailDomain')
MAILS_VIRTUAL_MAILALIAS = getattr(settings, 'MAILS_VIRTUAL_DOMAIN_MODEL', 'mails.MailAlias')
