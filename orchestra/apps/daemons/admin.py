from django.contrib import admin

from .models import Daemon, Host, Instance


class InstanceInline(admin.TabularInline):
    model = Instance


class DaemonAdmin(admin.ModelAdmin):
    inlines = [InstanceInline]


admin.site.register(Daemon, DaemonAdmin)
admin.site.register(Host)
