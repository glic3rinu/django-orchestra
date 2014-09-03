from django import forms
from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _

from orchestra.admin import AtLeastOneRequiredInlineFormSet
from orchestra.admin.utils import insertattr
from orchestra.apps.accounts.admin import AccountAdmin, AccountAdminMixin
from orchestra.forms.widgets import paddingCheckboxSelectMultiple
from .filters import HasInvoiceContactListFilter
from .models import Contact, InvoiceContact


class ContactAdmin(AccountAdminMixin, admin.ModelAdmin):
    list_display = (
        'short_name', 'full_name', 'email', 'phone', 'phone2', 'country',
        'account_link'
    )
    list_filter = ('email_usage',)
    search_fields = (
        'contact__user__username', 'short_name', 'full_name', 'phone', 'phone2',
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
            'fields': ('phone', 'phone_alternative'),
        }),
        (_("Postal address"), {
            'classes': ('wide',),
            'fields': ('address', ('zip_code', 'city'), 'country')
        }),
    )
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'address':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 2})
        if db_field.name == 'email_usage':
            kwargs['widget'] = paddingCheckboxSelectMultiple(130)
        return super(ContactAdmin, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(Contact, ContactAdmin)


class InvoiceContactInline(admin.StackedInline):
    model = InvoiceContact
    fields = ('name', 'address', ('city', 'zipcode'), 'country', 'vat')
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'address':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 2})
        if db_field.name == 'email_usage':
            kwargs['widget'] = paddingCheckboxSelectMultiple(45)
        return super(InvoiceContactInline, self).formfield_for_dbfield(db_field, **kwargs)


class ContactInline(InvoiceContactInline):
    model = Contact
    formset = AtLeastOneRequiredInlineFormSet
    extra = 0
    fields = (
        'short_name', 'full_name', 'email', 'email_usage', ('phone', 'phone2'),
        'address', ('city', 'zipcode'), 'country',
    )
    
    def get_extra(self, request, obj=None, **kwargs):
       return 0 if obj and obj.contacts.exists() else 1


def has_invoice(account):
    try:
        account.invoicecontact
    except InvoiceContact.DoesNotExist:
        return False
    return True
has_invoice.boolean = True
has_invoice.admin_order_field = 'invoicecontact'


insertattr(AccountAdmin, 'inlines', ContactInline)
insertattr(AccountAdmin, 'inlines', InvoiceContactInline)
insertattr(AccountAdmin, 'list_display', has_invoice)
insertattr(AccountAdmin, 'list_filter', HasInvoiceContactListFilter)
search_fields = (
    'contacts__short_name', 'contacts__full_name', 'contacts__phone',
    'contacts__phone2', 'contacts__email'
)
for field in search_fields:
    insertattr(AccountAdmin, 'search_fields', field)
