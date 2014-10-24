from django import forms
from django.contrib.auth import forms as auth_forms
from django.utils.translation import ugettext, ugettext_lazy as _

from .. import settings
from ..core.validators import validate_password


class PluginDataForm(forms.ModelForm):
    class Meta:
        exclude = ('data',)
    
    def __init__(self, *args, **kwargs):
        super(PluginDataForm, self).__init__(*args, **kwargs)
        # TODO remove it weel
        try:
            self.fields[self.plugin_field].widget = forms.HiddenInput()
        except KeyError:
            pass
        instance = kwargs.get('instance')
        if instance:
            for field in self.declared_fields:
                initial = self.fields[field].initial
                self.fields[field].initial = instance.data.get(field, initial)
    
    def save(self, commit=True):
        plugin = self.plugin
        setattr(self.instance, self.plugin_field, plugin.get_plugin_name())
        self.instance.data = {
            field: self.cleaned_data[field] for field in self.declared_fields
        }
        return super(PluginDataForm, self).save(commit=commit)


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
        widget=forms.PasswordInput, validators=[validate_password])
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))
    
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        if settings.ORCHESTRA_MIGRATION_MODE:
            self.fields['password1'].widget = forms.TextInput(attrs={'size':'130'})
            self.fields['password1'].help_text = _("RAW password digest (migration mode is enabled).")
            self.fields['password2'].widget = forms.HiddenInput()
            self.fields['password2'].required = False
    
    def clean_password2(self):
        if settings.ORCHESTRA_MIGRATION_MODE:
            return self.cleaned_data.get('password1')
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
        if settings.ORCHESTRA_MIGRATION_MODE:
            user.password = self.cleaned_data['password1']
        else:
            user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = auth_forms.ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))
    
    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
