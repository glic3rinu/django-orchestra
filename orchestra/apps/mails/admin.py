from django.contrib import admin

from .models import MailDomain, Mailbox, MailAlias


admin.site.register(MailDomain)
admin.site.register(Mailbox)
admin.site.register(MailAlias)
