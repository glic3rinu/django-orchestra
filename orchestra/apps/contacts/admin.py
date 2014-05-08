from django import forms
from django.contrib import admin

from orchestra.admin import AtLeastOneRequiredInlineFormSet
from orchestra.admin.utils import insertattr
from orchestra.apps.accounts.admin import AccountAdmin, AccountAdminMixin

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


admin.site.register(Contact, ContactAdmin)


class InvoiceContactInline(admin.StackedInline):
    model = InvoiceContact
    fields = ('name', 'address', ('city', 'zipcode'), 'country', 'vat')
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'address':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 2})
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
        account.invoicecontact.get()
    except InvoiceContact.DoesNotExist:
        return False
    return True
has_invoice.boolean = True
has_invoice.admin_order_field = 'invoicecontact'


insertattr(AccountAdmin, 'inlines', ContactInline)
insertattr(AccountAdmin, 'inlines', InvoiceContactInline)
insertattr(AccountAdmin, 'list_display', has_invoice)
insertattr(AccountAdmin, 'list_filter', HasInvoiceContactListFilter)
for field in ('contacts__short_name', 'contacts__full_name', 'contacts__phone',
              'contacts__phone2', 'contacts__email'):
    insertattr(AccountAdmin, 'search_fields', field)
