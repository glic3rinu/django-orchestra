from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.core.validators import validate_password

from .models import DatabaseUser, Database, Role


class DatabaseUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), required=False,
        widget=forms.PasswordInput, validators=[validate_password])
    password2 = forms.CharField(label=_("Password confirmation"), required=False,
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))
    
    class Meta:
        model = DatabaseUser
        fields = ('username', 'account', 'type')
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            msg = _("The two password fields didn't match.")
            raise forms.ValidationError(msg)
        return password2
    
    def save(self, commit=True):
        user = super(DatabaseUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class DatabaseCreationForm(DatabaseUserCreationForm):
    username = forms.RegexField(label=_("Username"), max_length=30,
        required=False, regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                    "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    user = forms.ModelChoiceField(required=False, queryset=DatabaseUser.objects)
    
    class Meta:
        model = Database
        fields = ('username', 'account', 'type')
    
    def __init__(self, *args, **kwargs):
        super(DatabaseCreationForm, self).__init__(*args, **kwargs)
        account_id = self.initial.get('account', None)
        if account_id:
            qs = self.fields['user'].queryset.filter(account=account_id)
            choices = [ (u.pk, "%s (%s)" % (u, u.get_type_display())) for u in qs ]
            self.fields['user'].queryset = qs
            self.fields['user'].choices = [(None, '--------'),] + choices
    
    def clean_password2(self):
        username = self.cleaned_data.get('username')
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if username and not (password1 and password2):
            raise forms.ValidationError(_("Missing password"))
        if password1 and password2 and password1 != password2:
            msg = _("The two password fields didn't match.")
            raise forms.ValidationError(msg)
        return password2
    
    def clean_user(self):
        user = self.cleaned_data.get('user')
        if user and user.type != self.cleaned_data.get('type'):
            msg = _("Database type and user type doesn't match")
            raise forms.ValidationError(msg)
        return user
    
    def clean(self):
        cleaned_data = super(DatabaseCreationForm, self).clean()
        if 'user' in cleaned_data and 'username' in cleaned_data:
            msg = _("Use existing user or create a new one?")
            if cleaned_data['user'] and self.cleaned_data['username']:
                raise forms.ValidationError(msg)
            elif not (cleaned_data['username'] or cleaned_data['user']):
                raise forms.ValidationError(msg)
        return cleaned_data
    
    def save(self, commit=True):
        db = super(DatabaseUserCreationForm, self).save(commit=False)
        user = self.cleaned_data['user']
        if commit:
            if not user:
                user = DatabaseUser(
                    username=self.cleaned_data['username'],
                    type=self.cleaned_data['type'],
                )
                user.set_password(self.cleaned_data["password1"])
            user.save()
            role, __ = Role.objects.get_or_create(database=db, user=user)
        return db


class ReadOnlySQLPasswordHashField(ReadOnlyPasswordHashField):
    class ReadOnlyPasswordHashWidget(forms.Widget):
        def render(self, name, value, attrs):
            original = ReadOnlyPasswordHashField.widget().render(name, value, attrs)
            if 'Invalid' not in original:
                return original
            encoded = value
            if not encoded:
                summary = mark_safe("<strong>%s</strong>" % _("No password set."))
            else:
                size = len(value)
                summary = value[:size/2] + '*'*(size-size/2)
                summary = "<strong>hash</strong>: %s" % summary
                if value.startswith('*'):
                    summary = "<strong>algorithm</strong>: sha1_bin_hex %s" % summary
            return format_html("<div>%s</div>" % summary)
    widget = ReadOnlyPasswordHashWidget


class DatabaseUserChangeForm(forms.ModelForm):
    password = ReadOnlySQLPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))
    
    class Meta:
        model = DatabaseUser
        fields = ('username', 'password', 'type', 'account')
    
    def clean_password(self):
        return self.initial["password"]
