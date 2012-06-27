from django import forms
from django.contrib import admin
from models import VirtualHost 
import settings


class VirtualHostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VirtualHostForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            # Add form
            self.fields['custom_directives'].initial = settings.DEFAULT_VIRTUAL_HOST_CUSTOM_DIRECTIVES


class VirtualHostAdmin(admin.ModelAdmin):
    list_display = ['ServerName','ServerAlias', 'DocumentRoot', 'ip', 'port',]
    list_filter = ['ip', 'port']
    search_fields = ['domains__domain__name', 'domains__subdomain__name',]
    fieldsets = ((None,     {'fields': (('ip', 'port'), 
                                    ('domains',),
                                    ('DocumentRoot'),
                                    ('redirect'),)}),
                 ('Custom Fields', {'classes': ('collapse',),
                                    'fields': (('custom_directives',),)}))
    filter_horizontal = ['domains']
    filter_fields_by_contact = ['domains']
    filter_unique_fields = ['domains']
    form = VirtualHostForm

    def change_view(self, *args, **kwargs):
        return super(VirtualHostAdmin, self).change_view(*args, **kwargs)


admin.site.register(VirtualHost, VirtualHostAdmin)
