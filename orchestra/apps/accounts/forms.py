from django import forms
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _

from orchestra.core.validators import validate_password
from orchestra.forms.widgets import ReadOnlyWidget

User = auth.get_user_model()


class AccountCreationForm(auth.forms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(AccountCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].validators.append(validate_password)
    
    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])
    
#    def save(self, commit=True):
#        account = super(auth.forms.UserCreationForm, self).save(commit=False)
#        account.set_password(self.cleaned_data['password1'])
#        if commit:
#            account.save()
#        return account


class AccountChangeForm(forms.ModelForm):
    username = forms.CharField()
    password = auth.forms.ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))
    
    def __init__(self, *args, **kwargs):
        super(AccountChangeForm, self).__init__(*args, **kwargs)
        account = kwargs.get('instance')
        self.fields['username'].widget = ReadOnlyWidget(account.username)
        self.fields['password'].initial = account.password
    
    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.fields['password'].initial
