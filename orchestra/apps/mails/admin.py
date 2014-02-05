from django.contrib import admin

from .models import MailDomain, Mailbox, MailAlias


class MailAliasAdmin(admin.ModelAdmin):
    pass


admin.site.register(MailDomain)
admin.site.register(Mailbox)
admin.site.register(MailAlias, MailAliasAdmin)
