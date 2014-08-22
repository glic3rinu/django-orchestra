from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import insertattr, admin_link
from orchestra.apps.accounts.admin import SelectAccountAdminMixin, AccountAdminMixin
from orchestra.apps.domains.forms import DomainIterator

from .filters import HasMailboxListFilter, HasForwardListFilter, HasAddressListFilter
from .models import Mailbox, Address, Autoresponse


class AutoresponseInline(admin.StackedInline):
    model = Autoresponse
    verbose_name_plural = _("autoresponse")
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'subject':
            kwargs['widget'] = forms.TextInput(attrs={'size':'118'})
        return super(AutoresponseInline, self).formfield_for_dbfield(db_field, **kwargs)


class MailboxAdmin(AccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'name', 'account_link', 'use_custom_filtering', 'display_addresses'
    )
    list_filter = ('use_custom_filtering', HasAddressListFilter)
    add_fieldsets = (
        (None, {
            'fields': ('account', 'name'),
        }),
        (_("Filtering"), {
            'fields': ('use_custom_filtering', 'custom_filtering'),
        }),
    )
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('account_link', 'name'),
        }),
        (_("Filtering"), {
            'classes': ('wide',),
            'fields': ('use_custom_filtering', 'custom_filtering'),
        }),
        (_("Addresses"), {
            'classes': ('wide',),
            'fields': ('addresses_field',)
        }),
    )
    readonly_fields = ('account_link', 'display_addresses', 'addresses_field')
    
    def display_addresses(self, mailbox):
        addresses = []
        for addr in mailbox.addresses.all():
            url = reverse('admin:mails_address_change', args=(addr.pk,))
            addresses.append('<a href="%s">%s</a>' % (url, addr.email))
        return '<br>'.join(addresses)
    display_addresses.short_description = _("Addresses")
    display_addresses.allow_tags = True
    
    def addresses_field(self, mailbox):
        """ Address form field with "Add address" button """
        account = mailbox.account
        add_url = reverse('admin:mails_address_add')
        add_url += '?account=%d&mailboxes=%s' % (account.pk, mailbox.pk)
        img = '<img src="/static/admin/img/icon_addlink.gif" width="10" height="10" alt="Add Another">'
        onclick = 'onclick="return showAddAnotherPopup(this);"'
        add_link = '<a href="%s" %s>%s Add address</a>' % (add_url, onclick, img)
        value = '%s<br><br>' % add_link
        for pk, name, domain in mailbox.addresses.values_list('pk', 'name', 'domain__name'):
            url = reverse('admin:mails_address_change', args=(pk,))
            name = '%s@%s' % (name, domain)
            value += '<li><a href="%s">%s</a></li>' % (url, name)
        value = '<ul>%s</ul>' % value
        return mark_safe('<div style="padding-left: 100px;">%s</div>' % value)
    addresses_field.short_description = _("Addresses")
    addresses_field.allow_tags = True


class AddressAdmin(SelectAccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'email', 'domain_link', 'display_mailboxes', 'display_forward', 'account_link'
    )
    list_filter = (HasMailboxListFilter, HasForwardListFilter)
    fields = ('account_link', ('name', 'domain'), 'mailboxes', 'forward')
    inlines = [AutoresponseInline]
    search_fields = ('name', 'domain__name',)
    readonly_fields = ('account_link', 'domain_link', 'email_link')
    filter_by_account_fields = ('domain', 'mailboxes')
    filter_horizontal = ['mailboxes']
    
    domain_link = admin_link('domain', order='domain__name')
    
    def email_link(self, address):
        link = self.domain_link(address)
        return "%s@%s" % (address.name, link)
    email_link.short_description = _("Email")
    email_link.allow_tags = True
    
    def display_mailboxes(self, address):
        boxes = []
        for mailbox in address.mailboxes.all():
            url = reverse('admin:mails_mailbox_change', args=(mailbox.pk,))
            boxes.append('<a href="%s">%s</a>' % (url, mailbox.name))
        return '<br>'.join(boxes)
    display_mailboxes.short_description = _("Mailboxes")
    display_mailboxes.allow_tags = True
    
    def display_forward(self, address):
        values = [ dest for dest in address.forward.split() ]
        return '<br>'.join(values)
    display_forward.short_description = _("Forward")
    display_forward.allow_tags = True
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'forward':
            kwargs['widget'] = forms.TextInput(attrs={'size':'118'})
        return super(AddressAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def get_queryset(self, request):
        """ Select related for performance """
        qs = super(AddressAdmin, self).get_queryset(request)
        return qs.select_related('domain')


admin.site.register(Mailbox, MailboxAdmin)
admin.site.register(Address, AddressAdmin)
