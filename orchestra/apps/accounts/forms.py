from django import forms
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _

from orchestra.core.validators import validate_password
from orchestra.forms.widgets import ReadOnlyWidget


class AccountCreationForm(auth.forms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(AccountCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].validators.append(validate_password)
    
    def clean_username(self):
        # Since model.clean() will check this, this is redundant,
        # but it sets a nicer error message than the ORM and avoids conflicts with contrib.auth
        username = self.cleaned_data["username"]
        account_model = self._meta.model
        if hasattr(account_model, 'systemusers'):
            systemuser_model = account_model.systemusers.related.model
            if systemuser_model.objects.filter(username=username).exists():
                raise forms.ValidationError(self.error_messages['duplicate_username'])
        return username


class AccountChangeForm(forms.ModelForm):
    password = auth.forms.ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))
    
    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
