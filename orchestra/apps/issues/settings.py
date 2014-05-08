from django.conf import settings


ISSUES_SUPPORT_EMAILS = getattr(settings, 'ISSUES_SUPPORT_EMAILS', [])


ISSUES_NOTIFY_SUPERUSERS = getattr(settings, 'ISSUES_NOTIFY_SUPERUSERS', True)
