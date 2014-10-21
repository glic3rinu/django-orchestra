from django import forms
from django.contrib.admin import widgets
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.forms import UserCreationForm, UserChangeForm
from orchestra.utils.python import AttrDict

from .models import Address, Mailbox


class MailboxForm(forms.ModelForm):
    """ hacky form for adding reverse M2M form field for Mailbox.addresses """
    addresses = forms.ModelMultipleChoiceField(queryset=Address.objects, required=False,
            widget=widgets.FilteredSelectMultiple(verbose_name=_('Pizzas'), is_stacked=False))
    
    def __init__(self, *args, **kwargs):
        super(MailboxForm, self).__init__(*args, **kwargs)
        field = AttrDict(**{
            'to': Address,
            'get_related_field': lambda: AttrDict(name='id'),
        })
        widget = self.fields['addresses'].widget
        self.fields['addresses'].widget = widgets.RelatedFieldWidgetWrapper(widget, field,
                self.modeladmin.admin_site, can_add_related=True)
        old_render = self.fields['addresses'].widget.render
        def render(*args, **kwargs):
            output = old_render(*args, **kwargs)
            args = 'account=%i' % self.modeladmin.account.pk
            output = output.replace('/add/?', '/add/?%s&' % args)
            return mark_safe(output)
        self.fields['addresses'].widget.render = render
        queryset = self.fields['addresses'].queryset
        self.fields['addresses'].queryset = queryset.filter(account=self.modeladmin.account.pk)
        
        if self.instance and self.instance.pk:
            self.fields['addresses'].initial = self.instance.addresses.all()
    
    def clean_custom_filtering(self):
        filtering = self.cleaned_data['filtering']
        custom_filtering = self.cleaned_data['custom_filtering']
        if filtering == self._meta.model.CUSTOM and not custom_filtering:
            raise forms.ValidationError(_("You didn't provide any custom filtering"))
        return custom_filtering



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
        if not cleaned_data.get('mailboxes', True) and not cleaned_data['forward']:
            raise forms.ValidationError(_("Mailboxes or forward address should be provided"))

