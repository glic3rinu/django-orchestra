import os
import textwrap

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orchestra.forms import UserCreationForm, UserChangeForm

from . import settings
from .models import SystemUser
from .validators import validate_home, validate_paths_exist


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
            self.fields['home'].widget.input_type = 'hidden'
            self.fields['directory'].widget.input_type = 'hidden'
        elif self.instance.pk and (self.instance.get_base_home() == self.instance.home):
            self.fields['directory'].widget = forms.HiddenInput()
        else:
            self.fields['directory'].widget = forms.TextInput(attrs={'size':'70'})
        if not self.instance.pk or not self.instance.is_main:
            # Some javascript for hidde home/directory inputs when convinient
            self.fields['shell'].widget.attrs['onChange'] = textwrap.dedent("""\
                field = $(".field-home, .field-directory");
                input = $("#id_home, #id_directory");
                if ($.inArray(this.value, %s) < 0) {
                    field.addClass("hidden");
                } else {
                   field.removeClass("hidden");
                   input.removeAttr("type");
                };""" % list(settings.SYSTEMUSERS_DISABLED_SHELLS)
            )
        self.fields['home'].widget.attrs['onChange'] = textwrap.dedent("""\
            field = $(".field-box.field-directory");
            input = $("#id_directory");
            if (this.value.search("%s") > 0) {
               field.addClass("hidden");
            } else {
               field.removeClass("hidden");
               input.removeAttr("type");
            };""" % username
        )
    
    def clean_directory(self):
        directory = self.cleaned_data['directory']
        return directory.lstrip('/')
    
    def clean(self):
        super(SystemUserFormMixin, self).clean()
        cleaned_data = self.cleaned_data
        home = cleaned_data.get('home')
        shell = cleaned_data.get('shell')
        if home and self.MOCK_USERNAME in home:
            username = cleaned_data.get('username', '')
            cleaned_data['home'] = home.replace(self.MOCK_USERNAME, username)
        elif home and shell not in settings.SYSTEMUSERS_DISABLED_SHELLS:
            cleaned_data['home'] = ''
            cleaned_data['directory'] = ''
        validate_home(self.instance, cleaned_data, self.account)
        return cleaned_data


class SystemUserCreationForm(SystemUserFormMixin, UserCreationForm):
    pass


class SystemUserChangeForm(SystemUserFormMixin, UserChangeForm):
    pass


class LinkForm(forms.Form):
    base_home = forms.ChoiceField(label=_("Target path"), choices=(),
        help_text=_("Target link will be under this directory."))
    home_extension = forms.CharField(label=_("Home extension"), required=False, initial='',
        widget=forms.TextInput(attrs={'size':'70'}),
        help_text=_("Relative path to chosen directory."))
    link_name = forms.CharField(label=_("Link name"), required=False, initial='',
        widget=forms.TextInput(attrs={'size':'70'}))
    
    def __init__(self, *args, **kwargs):
        self.instance = args[0]
        self.queryset = kwargs.pop('queryset', [])
        super_args = []
        if len(args) > 1:
            super_args.append(args[1])
        super(LinkForm, self).__init__(*super_args, **kwargs)
        related_users = type(self.instance).objects.filter(account=self.instance.account_id)
        self.fields['base_home'].choices = (
            (user.get_base_home(), user.get_base_home()) for user in related_users
        )
        if len(self.queryset) == 1:
            user = self.instance
            help_text = _("If left blank or relative path: the link will be created in %s home.") % user
        else:
            help_text = _("If left blank or relative path: the link will be created in each user home.")
        self.fields['link_name'].help_text = help_text
    
    def clean_home_extension(self):
        home_extension = self.cleaned_data['home_extension']
        return home_extension.lstrip('/')
    
    def clean_link_name(self):
        link_name = self.cleaned_data['link_name']
        if link_name:
            if link_name.startswith('/'):
                if len(self.queryset) > 1:
                    raise ValidationError(
                        _("Link name can not be a full path when multiple users."))
                link_names = [os.path.dirname(link_name)]
            else:
                dir_name = os.path.dirname(link_name)
                link_names = [os.path.join(user.home, dir_name) for user in self.queryset]
            validate_paths_exist(self.instance, link_names)
        return link_name
    
    def clean(self):
        cleaned_data = super(LinkForm, self).clean()
        path = os.path.join(cleaned_data['base_home'], cleaned_data['home_extension'])
        try:
            validate_paths_exist(self.instance, [path])
        except ValidationError as err:
            raise ValidationError({
                'home_extension': err,
            })
        return cleaned_data


class PermissionForm(LinkForm):
    set_action = forms.ChoiceField(label=_("Action"), initial='grant',
        choices=(
            ('grant', _("Grant")),
            ('revoke', _("Revoke"))
        ))
    base_home = forms.ChoiceField(label=_("Set permissions to"), choices=(),
        help_text=_("User will be granted/revoked access to this directory."))
    home_extension = forms.CharField(label=_("Home extension"), required=False, initial='',
        widget=forms.TextInput(attrs={'size':'70'}), help_text=_("Relative to chosen home."))
    permissions = forms.ChoiceField(label=_("Permissions"), initial='read-write',
        choices=(
            ('rw', _("Read and write")),
            ('r', _("Read only")),
            ('w', _("Write only"))
        ))
