from django import forms
from django.contrib.admin import widgets
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.forms import UserCreationForm, UserChangeForm
from orchestra.utils.python import AttrDict

from . import settings
from .models import Address, Mailbox


class MailboxForm(forms.ModelForm):
    """ hacky form for adding reverse M2M form field for Mailbox.addresses """
    # TODO keep track of this ticket for future reimplementation
    #      https://code.djangoproject.com/ticket/897
    addresses = forms.ModelMultipleChoiceField(queryset=Address.objects.select_related('domain'),
        required=False,
        widget=widgets.FilteredSelectMultiple(verbose_name=_('addresses'), is_stacked=False))
    
    def __init__(self, *args, **kwargs):
        super(MailboxForm, self).__init__(*args, **kwargs)
        # Hack the widget in order to display add button
        field = AttrDict(**{
            'to': Address,
            'get_related_field': lambda: AttrDict(name='id'),
        })
        widget = self.fields['addresses'].widget
        self.fields['addresses'].widget = widgets.RelatedFieldWidgetWrapper(widget, field,
                self.modeladmin.admin_site, can_add_related=True)
        
        # Filter related addresses by account
        old_render = self.fields['addresses'].widget.render
        def render(*args, **kwargs):
            output = old_render(*args, **kwargs)
            args = 'account=%i' % self.modeladmin.account.pk
            output = output.replace('/add/?', '/add/?%s&' % args)
            return mark_safe(output)
        self.fields['addresses'].widget.render = render
        queryset = self.fields['addresses'].queryset
        realted_addresses = queryset.filter(account_id=self.modeladmin.account.pk).order_by('name')
        self.fields['addresses'].queryset = realted_addresses
        
        if self.instance and self.instance.pk:
            self.fields['addresses'].initial = self.instance.addresses.all()
    
    def clean(self):
        cleaned_data = super(MailboxForm, self).clean()
        name = self.instance.name if self.instance.pk else cleaned_data.get('name')
        local_domain = settings.MAILBOXES_LOCAL_DOMAIN
        if name and local_domain:
            try:
                addr = Address.objects.get(name=name, domain__name=local_domain, account_id=self.modeladmin.account.pk)
            except Address.DoesNotExist:
                pass
            else:
                if addr not in cleaned_data.get('addresses', []):
                    raise ValidationError({
                        'addresses': _("This mailbox matches local address '%s', "
                                       "please make explicit this fact by selecting it.") % addr
                    })
        return cleaned_data


class MailboxChangeForm(UserChangeForm, MailboxForm):
    pass


class MailboxCreationForm(UserCreationForm, MailboxForm):
    def clean_name(self):
        # Since model.clean() will check this, this is redundant,
        # but it sets a nicer error message than the ORM and avoids conflicts with contrib.auth
        name = self.cleaned_data["name"]
        try:
            self._meta.model._default_manager.get(name=name)
        except self._meta.model.DoesNotExist:
            return name
        raise forms.ValidationError(self.error_messages['duplicate_username'])


class AddressForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(AddressForm, self).clean()
        forward = cleaned_data.get('forward', '')
        if not cleaned_data.get('mailboxes', True) and not forward:
            raise ValidationError(_("Mailboxes or forward address should be provided."))
        # Check if new addresse matches with a mbox because of having a local domain
        if self.instance.pk:
            name = self.instance.name
            domain = self.instance.domain
        else:
            name = cleaned_data.get('name')
            domain = cleaned_data.get('domain')
        if domain and name and domain.name == settings.MAILBOXES_LOCAL_DOMAIN:
            if name not in forward.split() and Mailbox.objects.filter(name=name).exists():
                for mailbox in cleaned_data.get('mailboxes', []):
                    if mailbox.name == name:
                        return
                raise ValidationError(
                    _("This address matches mailbox '%s', please make explicit this fact "
                      "by adding the mailbox on the mailboxes or forward field.") % name
                )
        return cleaned_data
