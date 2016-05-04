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
    addresses = forms.ModelMultipleChoiceField(required=False,
        queryset=Address.objects.select_related('domain'),
        widget=widgets.FilteredSelectMultiple(verbose_name=_('addresses'), is_stacked=False))
    
    def __init__(self, *args, **kwargs):
        super(MailboxForm, self).__init__(*args, **kwargs)
        # Hack the widget in order to display add button
        remote_field_mock = AttrDict(**{
            'model': Address,
            'get_related_field': lambda: AttrDict(name='id'),
            
        })
        widget = self.fields['addresses'].widget
        self.fields['addresses'].widget = widgets.RelatedFieldWidgetWrapper(
            widget, remote_field_mock, self.modeladmin.admin_site, can_add_related=True)
        
        account = self.modeladmin.account
        # Filter related addresses by account
        old_render = self.fields['addresses'].widget.render
        def render(*args, **kwargs):
            output = old_render(*args, **kwargs)
            args = 'account=%i&mailboxes=%s' % (account.pk, self.instance.pk)
            output = output.replace('/add/?', '/add/?%s&' % args)
            return mark_safe(output)
        self.fields['addresses'].widget.render = render
        queryset = self.fields['addresses'].queryset
        realted_addresses = queryset.filter(account_id=account.pk).order_by('name')
        self.fields['addresses'].queryset = realted_addresses
        
        if self.instance and self.instance.pk:
            self.fields['addresses'].initial = self.instance.addresses.all()
    
    def clean_name(self):
        name = self.cleaned_data['name']
        max_length = settings.MAILBOXES_NAME_MAX_LENGTH
        if len(name) > max_length:
            raise ValidationError("Name length should be less than %i." % max_length)
        return name


class MailboxChangeForm(UserChangeForm, MailboxForm):
    pass


class MailboxCreationForm(UserCreationForm, MailboxForm):
    def clean_name(self):
        # Since model.clean() will check this, this is redundant,
        # but it sets a nicer error message than the ORM and avoids conflicts with contrib.auth
        name = super().clean_name()
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
