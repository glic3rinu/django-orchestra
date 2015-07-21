from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import AtLeastOneRequiredInlineFormSet, ExtendedModelAdmin
from orchestra.admin.actions import SendEmail
from orchestra.admin.utils import insertattr, change_url
from orchestra.contrib.accounts.actions import list_accounts
from orchestra.contrib.accounts.admin import AccountAdmin, AccountAdminMixin
from orchestra.forms.widgets import paddingCheckboxSelectMultiple

from .filters import EmailUsageListFilter
from .models import Contact


class ContactAdmin(AccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'dispaly_name', 'email', 'phone', 'phone2', 'country', 'account_link'
    )
    # TODO email usage custom filter contains
    list_filter = (EmailUsageListFilter,)
    search_fields = (
        'account__username', 'account__full_name', 'short_name', 'full_name', 'phone', 'phone2',
        'email'
    )
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('account_link', 'short_name', 'full_name')
        }),
        (_("Email"), {
            'classes': ('wide',),
            'fields': ('email', 'email_usage',)
        }),
        (_("Phone"), {
            'classes': ('wide',),
            'fields': ('phone', 'phone2'),
        }),
        (_("Postal address"), {
            'classes': ('wide',),
            'fields': ('address', ('zipcode', 'city'), 'country')
        }),
    )
    # TODO don't repeat all only for account_link do it on accountadmin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('account', 'short_name', 'full_name')
        }),
        (_("Email"), {
            'classes': ('wide',),
            'fields': ('email', 'email_usage',)
        }),
        (_("Phone"), {
            'classes': ('wide',),
            'fields': ('phone', 'phone2'),
        }),
        (_("Postal address"), {
            'classes': ('wide',),
            'fields': ('address', ('zipcode', 'city'), 'country')
        }),
    )
    actions = (SendEmail(), list_accounts)
    
    def dispaly_name(self, contact):
        return str(contact)
    dispaly_name.short_description = _("Name")
    dispaly_name.admin_order_field = 'short_name'
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'address':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 2})
        if db_field.name == 'email_usage':
            kwargs['widget'] = paddingCheckboxSelectMultiple(130)
        return super(ContactAdmin, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(Contact, ContactAdmin)


class ContactInline(admin.StackedInline):
    model = Contact
    formset = AtLeastOneRequiredInlineFormSet
    extra = 0
    fields = (
        ('short_name', 'full_name'), 'email', 'email_usage', ('phone', 'phone2'),
    )
    
    def get_extra(self, request, obj=None, **kwargs):
       return 0 if obj and obj.contacts.exists() else 1
    
    def get_view_on_site_url(self, obj=None):
        if obj:
            return change_url(obj)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'short_name':
            kwargs['widget'] = forms.TextInput(attrs={'size':'15'})
        if db_field.name == 'address':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 2})
        if db_field.name == 'email_usage':
            kwargs['widget'] = paddingCheckboxSelectMultiple(45)
        return super(ContactInline, self).formfield_for_dbfield(db_field, **kwargs)


insertattr(AccountAdmin, 'inlines', ContactInline)
search_fields = (
    'contacts__short_name', 'contacts__full_name',
)
for field in search_fields:
    insertattr(AccountAdmin, 'search_fields', field)
