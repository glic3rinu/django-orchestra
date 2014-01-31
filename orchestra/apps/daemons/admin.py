from django.contrib import admin

from .models import Daemon, Instance


class InstanceInline(admin.TabularInline):
    model = Instance


class DaemonAdmin(admin.ModelAdmin):
    inlines = [InstanceInline]


admin.site.register(Daemon, DaemonAdmin)
