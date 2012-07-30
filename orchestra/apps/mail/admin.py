from actions import create_virtualdomain, delete_virtualdomain
from common.admin import AddOrChangeInlineFormMixin
from common.utils.admin import insert_inline, insert_list_filter, insert_list_display, insert_action
from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from dns.names.models import Name
from models import VirtualDomain, VirtualUser, VirtualAliase 


class VirtualDomainInlineForm(forms.ModelForm):
    mail_domain = forms.BooleanField(label='Mail domain', required=False)
    
    class Meta:
        model = VirtualDomain
        fields = ('mail_domain', 'type')
    
    def __init__(self, *args, **kwargs):
        super(VirtualDomainInlineForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['mail_domain'].initial = True

    def save(self, commit=True):
        """ Deletes virtualDomain if mail_domain is unmarked """
        if self.instance.pk and commit:
            if not self.cleaned_data['mail_domain']:
                VirtualDomain.objects.get(pk=self.instance.pk).delete()
        else:
            return super(VirtualDomainInlineForm, self).save(commit=commit)


class VirtualDomainInline(admin.TabularInline):
    model = VirtualDomain
    form = VirtualDomainInlineForm


class VirtualDomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'type']
    list_filter = ['type']


class VirtualUserAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'user', 'emailname', 'domain', 'address']
    filter_fields_by_contact = ['domain__domain', 'user']
    filter_unique_fields = ['user']


class VirtualAliaseForm(forms.ModelForm):
    destination = forms.CharField(label='Destination', widget=forms.widgets.TextInput(attrs={'size':'200'}))

    class Meta:
        model = VirtualAliase


class VirtualAliaseAdmin(admin.ModelAdmin):
    list_display = ['source', 'destination']
    fieldsets = (('Source',      {'fields': (('emailname', 'domain'),)},),
                 ('Destination', {'fields': (('destination',),),}),)
    filter_fields_by_contact = ['domain__domain']
    form = VirtualAliaseForm


admin.site.register(VirtualDomain, VirtualDomainAdmin)
admin.site.register(VirtualUser, VirtualUserAdmin)
admin.site.register(VirtualAliase, VirtualAliaseAdmin)


class ChangeVirtualUserInlineForm(forms.ModelForm):
    class Meta:
        model = VirtualUser


class AddVirtualUserInlineForm(ChangeVirtualUserInlineForm):
    class Meta:
        exclude = ('active')


#TODO: this doesn't work with contactsupportmixin
class VirtualUserTabularInline(admin.TabularInline, AddOrChangeInlineFormMixin):
    model = VirtualUser
    add_form = AddVirtualUserInlineForm
    change_form = ChangeVirtualUserInlineForm
    filter_fields_by_contact = ('domain__domain',)

insert_inline(User, VirtualUserTabularInline)    
insert_inline(Name, VirtualDomainInline)


class VirtualUserFilter(SimpleListFilter):
    title = _('Virtual User')
    parameter_name = 'viruser'

    def lookups(self, request, model_admin):
        return (
            ('Yes', _('Yes')),
            ('No', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(virtualuser__isnull=False)
        if self.value() == 'No':
            return queryset.filter(virtualuser__isnull=True)

insert_list_filter(User, VirtualUserFilter)


def virtual_user_status(self):
    return  hasattr(self, 'virtualuser')
virtual_user_status.short_description = _("Virtual User")
virtual_user_status.boolean = True
virtual_user_status.admin_order_field = 'virtualuser'

insert_list_display(User, virtual_user_status)


def virtual_domain(self):
    return hasattr(self, 'virtualdomain')
virtual_domain.short_description = _("Virtual Domain")
virtual_domain.admin_order_field = 'virtualdomain'
virtual_domain.boolean = True

insert_list_display(Name, virtual_domain)


insert_action(Name, create_virtualdomain)
insert_action(Name, delete_virtualdomain)


class VirtualDomainFilter(SimpleListFilter):
    title = _('Virtual Domain')
    parameter_name = 'virdomain'

    def lookups(self, request, model_admin):
        return (
            ('Yes', _('Yes')),
            ('No', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(virtualdomain__isnull=False)
        if self.value() == 'No':
            return queryset.filter(virtualdomain__isnull=True)

insert_list_filter(Name, VirtualDomainFilter)
