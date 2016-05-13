import copy
from urllib.parse import parse_qs

from django import forms
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.db.models import F, Count, Value as V
from django.db.models.functions import Concat
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin, ChangePasswordAdminMixin
from orchestra.admin.actions import disable, enable
from orchestra.admin.utils import admin_link, change_url
from orchestra.contrib.accounts.actions import list_accounts
from orchestra.contrib.accounts.admin import SelectAccountAdminMixin
from orchestra.contrib.accounts.filters import IsActiveListFilter
from orchestra.core import caches

from . import settings
from .actions import SendMailboxEmail, SendAddressEmail
from .filters import HasMailboxListFilter, HasForwardListFilter, HasAddressListFilter
from .forms import MailboxCreationForm, MailboxChangeForm, AddressForm
from .models import Mailbox, Address, Autoresponse
from .widgets import OpenCustomFilteringOnSelect


class AutoresponseInline(admin.StackedInline):
    model = Autoresponse
    verbose_name_plural = _("autoresponse")
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'subject':
            kwargs['widget'] = forms.TextInput(attrs={'size':'118'})
        return super(AutoresponseInline, self).formfield_for_dbfield(db_field, **kwargs)


class MailboxAdmin(ChangePasswordAdminMixin, SelectAccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'name', 'account_link', 'display_filtering', 'display_addresses', 'display_active',
    )
    list_filter = (IsActiveListFilter, HasAddressListFilter, 'filtering')
    search_fields = (
        'account__username', 'account__short_name', 'account__full_name', 'name',
        'addresses__name', 'addresses__domain__name',
    )
    add_fieldsets = (
        (None, {
            'fields': ('account_link', 'name', 'password1', 'password2', 'filtering'),
        }),
        (_("Custom filtering"), {
            'classes': ('collapse',),
            'description': _("Please remember to select <tt>custom filtering</tt> "
                             "if you want this filter to be applied."),
            'fields': ('custom_filtering',),
        }),
        (_("Addresses"), {
            'fields': ('addresses',)
        }),
    )
    fieldsets = (
        (None, {
            'fields': ('name', 'password', 'is_active', 'account_link', 'filtering'),
        }),
        (_("Custom filtering"), {
            'classes': ('collapse',),
            'fields': ('custom_filtering',),
        }),
        (_("Addresses"), {
            'fields': ('addresses', 'display_forwards')
        }),
    )
    readonly_fields = ('account_link', 'display_addresses', 'display_forwards')
    change_readonly_fields = ('name',)
    add_form = MailboxCreationForm
    form = MailboxChangeForm
    list_prefetch_related = ('addresses__domain',)
    actions = (disable, enable, list_accounts)
    
    def __init__(self, *args, **kwargs):
        super(MailboxAdmin, self).__init__(*args, **kwargs)
        if settings.MAILBOXES_LOCAL_DOMAIN:
            type(self).actions = self.actions + (SendMailboxEmail(),)
    
    def display_addresses(self, mailbox):
        # Get from forwards
        cache = caches.get_request_cache()
        cached_forwards = cache.get('forwards')
        if cached_forwards is None:
            cached_forwards = {}
            qs = Address.objects.filter(forward__regex=r'(^|.*\s)[^@]+(\s.*|$)')
            qs = qs.annotate(email=Concat('name', V('@'), 'domain__name'))
            qs = qs.values_list('id', 'email', 'forward')
            for addr_id, email, mbox in qs:
                url = reverse('admin:mailboxes_address_change', args=(addr_id,))
                link = '<a href="%s">%s</a>' % (url, email)
                try:
                    cached_forwards[mbox].append(link)
                except KeyError:
                    cached_forwards[mbox] = [link]
            cache.set('forwards', cached_forwards)
        try:
            forwards = cached_forwards[mailbox.name]
        except KeyError:
            forwards = []
        # Get from mailboxes
        addresses = []
        for addr in mailbox.addresses.all():
            url = change_url(addr)
            addresses.append('<a href="%s">%s</a>' % (url, addr.email))
        return '<br>'.join(addresses+forwards)
    display_addresses.short_description = _("Addresses")
    display_addresses.allow_tags = True
    
    def display_forwards(self, mailbox):
        forwards = []
        for addr in mailbox.get_forwards():
            url = change_url(addr)
            forwards.append('<a href="%s">%s</a>' % (url, addr.email))
        return '<br>'.join(forwards)
    display_forwards.short_description = _("Forward from")
    display_forwards.allow_tags = True
    
    def display_filtering(self, mailbox):
        """ becacuse of allow_tags = True """
        return mailbox.get_filtering_display()
    display_filtering.short_description = _("Filtering")
    display_filtering.admin_order_field = 'filtering'
    display_filtering.allow_tags = True
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'filtering':
            kwargs['widget'] = OpenCustomFilteringOnSelect()
        return super(MailboxAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super(MailboxAdmin, self).get_fieldsets(request, obj)
        if obj and obj.filtering == obj.CUSTOM:
            # not collapsed filtering when exists
            fieldsets = copy.deepcopy(fieldsets)
            fieldsets[1][1]['classes'] = fieldsets[0][1]['fields'] + ('collapse', 'open',)
        elif '_to_field' in parse_qs(request.META['QUERY_STRING']):
            # remove address from popup
            fieldsets = list(copy.deepcopy(fieldsets))
            fieldsets.pop(-1)
        return fieldsets
    
    def get_form(self, *args, **kwargs):
        form = super(MailboxAdmin, self).get_form(*args, **kwargs)
        form.modeladmin = self
        return form
    
    def get_search_results(self, request, queryset, search_term):
        # Remove local domain from the search term if present (implicit local addreç)
        search_term = search_term.replace('@'+settings.MAILBOXES_LOCAL_DOMAIN, '')
        # Split address name from domain in order to support address searching
        search_term = search_term.replace('@', ' ')
        return super(MailboxAdmin, self).get_search_results(request, queryset, search_term)
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not add:
            self.check_unrelated_address(request, obj)
            self.check_matching_address(request, obj)
        return super(MailboxAdmin, self).render_change_form(
            request, context, add, change, form_url, obj)
    
    def log_addition(self, request, object, *args, **kwargs):
        self.check_unrelated_address(request, object)
        self.check_matching_address(request, object)
        return super(MailboxAdmin, self).log_addition(request, object, *args, **kwargs)
    
    def check_matching_address(self, request, obj):
        local_domain = settings.MAILBOXES_LOCAL_DOMAIN
        if obj.name and local_domain:
            try:
                addr = Address.objects.get(
                    name=obj.name, domain__name=local_domain, account_id=self.account.pk)
            except Address.DoesNotExist:
                pass
            else:
                if addr not in obj.addresses.all():
                    msg =  _("Mailbox '%s' local address matches '%s', please consider if "
                             "selecting it makes sense.") % (obj, addr)
                    if msg not in (m.message for m in messages.get_messages(request)):
                        self.message_user(request, msg, level=messages.WARNING)
    
    def check_unrelated_address(self, request, obj):
        # Check if there exists an unrelated local Address for this mbox
        local_domain = settings.MAILBOXES_LOCAL_DOMAIN
        if local_domain and obj.name:
            non_mbox_addresses = Address.objects.exclude(mailboxes__name=obj.name).exclude(
                forward__regex=r'.*(^|\s)+%s($|\s)+.*' % obj.name)
            try:
                addr = non_mbox_addresses.get(name=obj.name, domain__name=local_domain)
            except Address.DoesNotExist:
                pass
            else:
                url = reverse('admin:mailboxes_address_change', args=(addr.pk,))
                msg = mark_safe(
                    _("Address <a href='{url}'>{addr}</a> clashes with '{mailbox}' mailbox "
                      "local address. Consider adding this mailbox to the address.").format(
                      mailbox=obj.name, url=url, addr=addr)
                )
                # Prevent duplication (add_view+continue)
                if msg not in (m.message for m in messages.get_messages(request)):
                    self.message_user(request, msg, level=messages.WARNING)
    
    def save_model(self, request, obj, form, change):
        """ save hacky mailbox.addresses and local domain clashing """
        if obj.filtering != obj.CUSTOM:
            msg = _("You have provided a custom filtering but filtering "
                    "selected option is %s") % obj.get_filtering_display()
            if change:
                old = Mailbox.objects.get(pk=obj.pk)
                if old.custom_filtering != obj.custom_filtering:
                    messages.warning(request, msg)
            elif obj.custom_filtering:
                messages.warning(request, msg)
        super(MailboxAdmin, self).save_model(request, obj, form, change)
        obj.addresses = form.cleaned_data['addresses']


class AddressAdmin(SelectAccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'display_email', 'account_link', 'domain_link', 'display_mailboxes', 'display_forward',
    )
    list_filter = (HasMailboxListFilter, HasForwardListFilter)
    fields = ('account_link', 'email_link', 'mailboxes', 'forward', 'display_all_mailboxes')
    add_fields = ('account_link', ('name', 'domain'), 'mailboxes', 'forward')
#    inlines = [AutoresponseInline]
    search_fields = (
        'forward', 'mailboxes__name', 'account__username', 'computed_email', 'domain__name'
    )
    readonly_fields = ('account_link', 'domain_link', 'email_link', 'display_all_mailboxes')
    actions = (SendAddressEmail(),)
    filter_by_account_fields = ('domain', 'mailboxes')
    filter_horizontal = ['mailboxes']
    form = AddressForm
    list_prefetch_related = ('mailboxes', 'domain')
    
    domain_link = admin_link('domain', order='domain__name')
    
    def display_email(self, address):
        return address.computed_email
    display_email.short_description = _("Email")
    display_email.admin_order_field = 'computed_email'
    
    def email_link(self, address):
        link = self.domain_link(address)
        return "%s@%s" % (address.name, link)
    email_link.short_description = _("Email")
    email_link.allow_tags = True
    
    def display_mailboxes(self, address):
        boxes = []
        for mailbox in address.mailboxes.all():
            url = change_url(mailbox)
            boxes.append('<a href="%s">%s</a>' % (url, mailbox.name))
        return '<br>'.join(boxes)
    display_mailboxes.short_description = _("Mailboxes")
    display_mailboxes.allow_tags = True
    display_mailboxes.admin_order_field = 'mailboxes__count'
    
    def display_all_mailboxes(self, address):
        boxes = []
        for mailbox in address.get_mailboxes():
            url = change_url(mailbox)
            boxes.append('<a href="%s">%s</a>' % (url, mailbox.name))
        return '<br>'.join(boxes)
    display_all_mailboxes.short_description = _("Mailboxes links")
    display_all_mailboxes.allow_tags = True
    
    def display_forward(self, address):
        forward_mailboxes = {m.name: m for m in address.get_forward_mailboxes()}
        values = []
        for forward in address.forward.split():
            mbox = forward_mailboxes.get(forward)
            if mbox:
                values.append(admin_link()(mbox))
            else:
                values.append(forward)
        return '<br>'.join(values)
    display_forward.short_description = _("Forward")
    display_forward.allow_tags = True
    display_forward.admin_order_field = 'forward'
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'forward':
            kwargs['widget'] = forms.TextInput(attrs={'size':'118'})
        return super(AddressAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def get_fields(self, request, obj=None):
        """ Remove mailboxes field when creating address from a popup i.e. from mailbox add form """
        fields = super(AddressAdmin, self).get_fields(request, obj)
        if '_to_field' in parse_qs(request.META['QUERY_STRING']):
            # Add address popup
            fields = list(fields)
            fields.remove('mailboxes')
        return fields
    
    def get_queryset(self, request):
        qs = super(AddressAdmin, self).get_queryset(request)
        qs = qs.annotate(computed_email=Concat(F('name'), V('@'), F('domain__name')))
        return qs.annotate(Count('mailboxes'))
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not add:
            self.check_matching_mailbox(request, obj)
        return super(AddressAdmin, self).render_change_form(
            request, context, add, change, form_url, obj)
    
    def log_addition(self, request, object, *args, **kwargs):
        self.check_matching_mailbox(request, object)
        return super(AddressAdmin, self).log_addition(request, object, *args, **kwargs)
    
    def check_matching_mailbox(self, request, obj):
        # Check if new addresse matches with a mbox because of having a local domain
        if obj.name and obj.domain and obj.domain.name == settings.MAILBOXES_LOCAL_DOMAIN:
            if obj.name not in obj.forward.split() and Mailbox.objects.filter(name=obj.name).exists():
                for mailbox in obj.mailboxes.all():
                    if mailbox.name == obj.name:
                        return
                msg = _("Address '%s' matches mailbox '%s' local address, please consider "
                        "if makes sense adding the mailbox on the mailboxes or forward field."
                       ) % (obj, obj.name)
                if msg not in (m.message for m in messages.get_messages(request)):
                    self.message_user(request, msg, level=messages.WARNING)


admin.site.register(Mailbox, MailboxAdmin)
admin.site.register(Address, AddressAdmin)
