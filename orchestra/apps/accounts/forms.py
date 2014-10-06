from django import forms
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _

from orchestra.core.validators import validate_password
from orchestra.forms import UserCreationForm
from orchestra.forms.widgets import ReadOnlyWidget



class AccountCreationForm(UserCreationForm):
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
