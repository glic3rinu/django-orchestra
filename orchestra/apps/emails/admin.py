from django.contrib import admin

from .models import Domain, Mailbox, Alias


admin.site.register(Domain)
admin.site.register(Mailbox)
admin.site.register(Alias)
