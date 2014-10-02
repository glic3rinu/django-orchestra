from django import forms
from django.contrib import auth
from django.utils.translation import ugettext, ugettext_lazy as _

from orchestra.apps.accounts.models import Account
from orchestra.core.validators import validate_password

from .models import SystemUser


# TODO orchestra.UserCretionForm
class UserCreationForm(auth.forms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].validators.append(validate_password)
    
    def clean_username(self):
        # Since model.clean() will check this, this is redundant,
        # but it sets a nicer error message than the ORM and avoids conflicts with contrib.auth
        username = self.cleaned_data["username"]
        try:
            SystemUser._default_manager.get(username=username)
        except SystemUser.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])



# TODO orchestra.UserCretionForm
class UserChangeForm(forms.ModelForm):
    password = auth.forms.ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))
    
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')
    
    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
