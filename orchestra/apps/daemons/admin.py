from common.utils.admin import UsedContentTypeFilter
from daemons.models import Host, Daemon, DaemonInstance
from django.contrib import admin, messages
from django.db import transaction
from django.utils.translation import ugettext as _


class DaemonInstanceInline(admin.TabularInline):
    model = DaemonInstance
    extra = 1


class DaemonAdmin(admin.ModelAdmin):
    list_display = ('name', 'content_type', 'save_template', 'save_method', 'delete_template', 'delete_method', 'active')
    list_filter = ['active', UsedContentTypeFilter]
    actions = ['disable_selected',]
    fieldsets = ((None,     {'fields': (('name', 'active'),)}),
                 ('Manager',{'fields': (('content_type'),
                                        )}),
                 ('Driver', {'fields': (('save_template', 'save_method'),
                                        ('delete_template', 'delete_method'),)}),)
    inlines = [DaemonInstanceInline]              
    actions = ['disable_selected','enable_selected']
    
    @transaction.commit_on_success
    def disable_selected(modeladmin, request, queryset):
        for daemon in queryset:
            daemon.disable()
        messages.add_message(request, messages.INFO, _("All Selected daemons has been disabled"))
        return

    @transaction.commit_on_success
    def enable_selected(modeladmin, request, queryset):
        for daemon in queryset:
            daemon.enable()
        messages.add_message(request, messages.INFO, _("All Selected daemons has been enabled"))
        return


class HostAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip', 'os')
    inlines = []


admin.site.register(Host, HostAdmin)
admin.site.register(Daemon, DaemonAdmin)

