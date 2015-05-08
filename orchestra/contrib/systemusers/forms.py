import textwrap

from django import forms
from django.utils.translation import ngettext, ugettext_lazy as _

from orchestra.forms import UserCreationForm, UserChangeForm

from . import settings
from .models import SystemUser
from .validators import validate_home


class SystemUserFormMixin(object):
    MOCK_USERNAME = '<username>'
    
    def __init__(self, *args, **kwargs):
        super(SystemUserFormMixin, self).__init__(*args, **kwargs)
        duplicate = lambda n: (n, n)
        if self.instance.pk:
            username = self.instance.username
            choices=(
                duplicate(self.account.main_systemuser.get_base_home()),
                duplicate(self.instance.get_base_home()),
            )
        else:
            username = self.MOCK_USERNAME
            choices=(
                duplicate(self.account.main_systemuser.get_base_home()),
                duplicate(SystemUser(username=username).get_base_home()),
            )
        self.fields['home'].widget = forms.Select(choices=choices)
        if self.instance.pk and (self.instance.is_main or self.instance.has_shell):
            # hidde home option for shell users
            self.fields['home'].widget = forms.HiddenInput()
            self.fields['directory'].widget = forms.HiddenInput()
        elif self.instance.pk and (self.instance.get_base_home() == self.instance.home):
            self.fields['directory'].widget = forms.HiddenInput()
        else:
            self.fields['directory'].widget = forms.TextInput(attrs={'size':'70'})
        if not self.instance.pk or not self.instance.is_main:
            # Some javascript for hidde home/directory inputs when convinient
            self.fields['shell'].widget.attrs = {
                'onChange': textwrap.dedent("""\
                    field = $(".field-home, .field-directory");
                    input = $("#id_home, #id_directory");
                    if ($.inArray(this.value, %s) < 0) {
                        field.addClass("hidden");
                    } else {
                       field.removeClass("hidden");
                       input.removeAttr("type");
                    };""" % str(list(settings.SYSTEMUSERS_DISABLED_SHELLS)))
            }
        self.fields['home'].widget.attrs = {
            'onChange': textwrap.dedent("""\
                field = $(".field-box.field-directory");
                input = $("#id_directory");
                if (this.value.search("%s") > 0) {
                   field.addClass("hidden");
                } else {
                   field.removeClass("hidden");
                   input.removeAttr("type");
                };""" % username)
        }
    
    def clean(self):
        super(SystemUserFormMixin, self).clean()
        home = self.cleaned_data.get('home')
        if home and self.MOCK_USERNAME in home:
            username = self.cleaned_data.get('username', '')
            self.cleaned_data['home'] = home.replace(self.MOCK_USERNAME, username)
        validate_home(self.instance, self.cleaned_data, self.account)


class SystemUserCreationForm(SystemUserFormMixin, UserCreationForm):
    pass


class SystemUserChangeForm(SystemUserFormMixin, UserChangeForm):
    pass


class GrantPermissionForm(forms.Form):
    base_path = forms.ChoiceField(label=_("Grant access to"), choices=(),
        help_text=_("User will be granted access to this directory."))
    path_extension = forms.CharField(label=_("Path extension"), required=False, initial='',
        widget=forms.TextInput(attrs={'size':'70'}), help_text=_("Relative to chosen home."))
    read_only = forms.BooleanField(label=_("Read only"), initial=False, required=False,
        help_text=_("Designates whether the permissions granted will be read-only or read/write."))
    
    def __init__(self, *args, **kwargs):
        instance = args[0]
        super_args = []
        if len(args) > 1:
            super_args.append(args[1])
        super(GrantPermissionForm, self).__init__(*super_args, **kwargs)
        related_users = type(instance).objects.filter(account=instance.account_id)
        self.fields['base_path'].choices = (
            (user.get_base_home(), user.get_base_home()) for user in related_users
        )
