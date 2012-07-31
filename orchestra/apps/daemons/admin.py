from common.utils.admin import UsedContentTypeFilter
from common.utils.file import list_files
from daemons.models import Host, Daemon, DaemonInstance
from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.utils.translation import ugettext as _
import settings


class DaemonInstanceInline(admin.TabularInline):
    model = DaemonInstance
    extra = 1


class DaemonForm(forms.ModelForm):
    """ dynamic retrieve of template choices """
    
    save_template = forms.ChoiceField(required=False)
    
    class Meta:
        model = Daemon

    def __init__(self, *args, **kwargs):
        super(DaemonForm, self).__init__(*args, **kwargs)
        template_choices = [('', '---------')] + list_files(settings.DAEMONS_TEMPLATE_PATHS)
        self.fields['save_template'].choices = template_choices
        self.fields['delete_template'].choices = template_choices


class DaemonAdmin(admin.ModelAdmin):
    list_display = ('name', 'content_type', 'save_template', 'save_method', 'delete_template', 'delete_method', 'active')
    list_filter = ['active', UsedContentTypeFilter]
    actions = ['disable_selected',]
    fieldsets = ((None,     {'fields': (('name', 'active'),
                                        ('content_type',),
                                        )}),
                 ('Driver', {'fields': (('save_template', 'save_method'),
                                        ('delete_template', 'delete_method'),)}),)
    inlines = [DaemonInstanceInline]              
    actions = ['disable_selected','enable_selected']
    form = DaemonForm
    
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
