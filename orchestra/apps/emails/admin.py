from django.contrib import admin

from .models import MailDomain, Mailbox, Alias


admin.site.register(MailDomain)
admin.site.register(Mailbox)
admin.site.register(Alias)
