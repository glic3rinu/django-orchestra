from django import forms
from django.contrib.auth import forms as auth_forms
from django.utils.translation import ugettext_lazy as _

from orchestra.utils.python import random_ascii

from ..core.validators import validate_password

from .fields import SpanField
from .widgets import SpanWidget


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'duplicate_username': _("A user with that username already exists."),
    }
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'off'}),
        validators=[validate_password])
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))
    
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].help_text = _("Suggestion: %s") % random_ascii(10)
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2
    
    def clean_username(self):
        # Since model.clean() will check this, this is redundant,
        # but it sets a nicer error message than the ORM and avoids conflicts with contrib.auth
        username = self.cleaned_data["username"]
        try:
            self._meta.model._default_manager.get(username=username)
        except self._meta.model.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])
    
    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = auth_forms.ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change it by "
                    "using <a href='../password/'>this form</a>. "
                    "<a onclick='return showAddAnotherPopup(this);' href='../hash/'>Show hash</a>."))
    
    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class NonStoredUserChangeForm(forms.ModelForm):
    password = forms.CharField(label=_("Password"), required=False,
        widget=SpanWidget(display='<strong>Unknown password</strong>'),
        help_text=_("This service's password is not stored, so there is no way to see it, "
                    "but you can change it using <a href=\"../password/\">this form</a>."))


class ReadOnlyFormMixin(object):
    """
    Mixin class for ModelForm or Form that provides support for SpanField on readonly fields
    Meta:
        readonly_fields = (ro_field1, ro_field2)
    """
    def __init__(self, *args, **kwargs):
        super(ReadOnlyFormMixin, self).__init__(*args, **kwargs)
        for name in self.Meta.readonly_fields:
            field = self.fields[name]
            if not isinstance(field, SpanField):
                if not isinstance(field.widget, SpanWidget):
                    field.widget = SpanWidget()
                original = self.initial.get(name)
                if hasattr(self, 'instance'):
                    original = getattr(self.instance, name, original)
                field.widget.original = original
