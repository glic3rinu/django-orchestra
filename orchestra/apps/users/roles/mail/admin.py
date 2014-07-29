from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import insertattr, admin_link
from orchestra.apps.accounts.admin import SelectAccountAdminMixin
from orchestra.apps.domains.forms import DomainIterator
from orchestra.apps.users.roles.admin import RoleAdmin

from .forms import MailRoleAdminForm
from .models import Mailbox, Address, Autoresponse


class AutoresponseInline(admin.StackedInline):
    model = Autoresponse
    verbose_name_plural = _("autoresponse")
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'subject':
            kwargs['widget'] = forms.TextInput(attrs={'size':'118'})
        return super(AutoresponseInline, self).formfield_for_dbfield(db_field, **kwargs)


#class AddressAdmin(SelectAccountAdminMixin, ExtendedModelAdmin):
#    list_display = ('email', 'domain_link', 'mailboxes', 'forwards', 'account_link')
#    fields = ('account_link', ('name', 'domain'), 'destination')
#    inlines = [AutoresponseInline]
#    search_fields = ('name', 'domain__name',)
#    readonly_fields = ('account_link', 'domain_link', 'email_link')
#    filter_by_account_fields = ['domain']
#    
#    domain_link = link('domain', order='domain__name')
#    
#    def email_link(self, address):
#        link = self.domain_link(address)
#        return "%s@%s" % (address.name, link)
#    email_link.short_description = _("Email")
#    email_link.allow_tags = True
#    
#    def mailboxes(self, address):
#        boxes = []
#        for mailbox in address.get_mailboxes():
#            user = mailbox.user
#            url = reverse('admin:users_user_mailbox_change', args=(user.pk,))
#            boxes.append('<a href="%s">%s</a>' % (url, user.username))
#        return '<br>'.join(boxes)
#    mailboxes.allow_tags = True
#    
#    def forwards(self, address):
#        values = [ dest for dest in address.destination.split() if '@' in dest ]
#        return '<br>'.join(values)
#    forwards.allow_tags = True
#    
#    def formfield_for_dbfield(self, db_field, **kwargs):
#        if db_field.name == 'destination':
#            kwargs['widget'] = forms.TextInput(attrs={'size':'118'})
#        return super(AddressAdmin, self).formfield_for_dbfield(db_field, **kwargs)
#    
#    def queryset(self, request):
#        """ Select related for performance """
#        qs = super(AddressAdmin, self).queryset(request)
#        # TODO django 1.7 account__user is not needed
#        return qs.select_related('domain', 'account__user')


class AddressAdmin(SelectAccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'email', 'domain_link', 'display_mailboxes', 'display_forward', 'account_link'
    )
    fields = ('account_link', ('name', 'domain'), 'mailboxes', 'forward')
    inlines = [AutoresponseInline]
    search_fields = ('name', 'domain__name',)
    readonly_fields = ('account_link', 'domain_link', 'email_link')
    filter_by_account_fields = ['domain']
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
            user = mailbox.user
            url = reverse('admin:users_user_mailbox_change', args=(user.pk,))
            boxes.append('<a href="%s">%s</a>' % (url, user.username))
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
        if db_field.name == 'mailboxes':
            mailboxes = db_field.rel.to.objects.select_related('user')
            kwargs['queryset'] = mailboxes.filter(user__account=self.account)
        return super(AddressAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def get_queryset(self, request):
        """ Select related for performance """
        qs = super(AddressAdmin, self).get_queryset(request)
        # TODO django 1.7 account__user is not needed
        return qs.select_related('domain', 'account__user')


class MailRoleAdmin(RoleAdmin):
    model = Mailbox
    name = 'mailbox'
    url_name = 'mailbox'
    form = MailRoleAdminForm


admin.site.register(Address, AddressAdmin)
insertattr(get_user_model(), 'roles', MailRoleAdmin)
