from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.forms.widgets import ReadOnlyWidget

from .models import Mailbox
from ..forms import RoleAdminBaseForm


class MailRoleAdminForm(RoleAdminBaseForm):
    class Meta(RoleAdminBaseForm.Meta):
        model = Mailbox
    
    def __init__(self, *args, **kwargs):
        super(MailRoleAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            widget = ReadOnlyWidget(self.addresses(instance))
            self.fields['addresses'] = forms.CharField(widget=widget,
                    label=_("Addresses"))
    
#    def addresses(self, mailbox):
#        account = mailbox.user.account
#        addresses = account.addresses.filter(destination__contains=mailbox.user.username)
#        add_url = reverse('admin:mail_address_add')
#        add_url += '?account=%d&destination=%s' % (account.pk, mailbox.user.username)
#        img = '<img src="/static/admin/img/icon_addlink.gif" width="10" height="10" alt="Add Another">'
#        onclick = 'onclick="return showAddAnotherPopup(this);"'
#        add_link = '<a href="%s" %s>%s Add address</a>' % (add_url, onclick, img)
#        value = '%s<br><br>' % add_link
#        for pk, name, domain in addresses.values_list('pk', 'name', 'domain__name'):
#            url = reverse('admin:mail_address_change', args=(pk,))
#            name = '%s@%s' % (name, domain)
#            value += '<li><a href="%s">%s</a></li>' % (url, name)
#        value = '<ul>%s</ul>' % value
#        return mark_safe('<div style="padding-left: 100px;">%s</div>' % value)

    def addresses(self, mailbox):
        account = mailbox.user.account
        add_url = reverse('admin:mail_address_add')
        add_url += '?account=%d&mailboxes=%s' % (account.pk, mailbox.pk)
        img = '<img src="/static/admin/img/icon_addlink.gif" width="10" height="10" alt="Add Another">'
        onclick = 'onclick="return showAddAnotherPopup(this);"'
        add_link = '<a href="%s" %s>%s Add address</a>' % (add_url, onclick, img)
        value = '%s<br><br>' % add_link
        for pk, name, domain in mailbox.addresses.values_list('pk', 'name', 'domain__name'):
            url = reverse('admin:mail_address_change', args=(pk,))
            name = '%s@%s' % (name, domain)
            value += '<li><a href="%s">%s</a></li>' % (url, name)
        value = '<ul>%s</ul>' % value
        return mark_safe('<div style="padding-left: 100px;">%s</div>' % value)
