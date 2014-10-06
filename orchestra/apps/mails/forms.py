from django import forms

from orchestra.forms import UserCreationForm


class MailboxCreationForm(UserCreationForm):
    def clean_name(self):
        # Since model.clean() will check this, this is redundant,
        # but it sets a nicer error message than the ORM and avoids conflicts with contrib.auth
        name = self.cleaned_data["name"]
        try:
            self._meta.model._default_manager.get(name=name)
        except self._meta.model.DoesNotExist:
            return name
        raise forms.ValidationError(self.error_messages['duplicate_name'])


class AddressForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(AddressForm, self).clean()
        if not cleaned_data['mailboxes'] and not cleaned_data['forward']:
            raise forms.ValidationError(_("Mailboxes or forward address should be provided"))
