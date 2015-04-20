from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from orchestra import plugins
from orchestra.contrib.orchestration import Operation
from orchestra.core import validators
from orchestra.forms import widgets
from orchestra.plugins.forms import PluginDataForm
from orchestra.utils.functional import cached
from orchestra.utils.python import import_class, random_ascii

from .. import settings


class SoftwareServiceForm(PluginDataForm):
    site_url = forms.CharField(label=_("Site URL"), widget=widgets.ShowTextWidget, required=False)
    password = forms.CharField(label=_("Password"), required=False,
        widget=widgets.ReadOnlyWidget('<strong>Unknown password</strong>'),
        validators=[
            RegexValidator(r'^[^"\'\\]+$',
                           _('Enter a valid password. '
                             'This value may contain any ascii character except for '
                             ' \'/"/\\/ characters.'), 'invalid'),
        ],
        help_text=_("Passwords are not stored, so there is no way to see this "
                    "service's password, but you can change the password using "
                    "<a href=\"password/\">this form</a>."))
    password1 = forms.CharField(label=_("Password"), validators=[validators.validate_password],
            widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
            widget=forms.PasswordInput,
            help_text=_("Enter the same password as above, for verification."))
    
    class Meta:
        exclude = ('database',)
    
    def __init__(self, *args, **kwargs):
        super(SoftwareServiceForm, self).__init__(*args, **kwargs)
        self.is_change = bool(self.instance and self.instance.pk)
        if self.is_change:
            site_domain = self.instance.get_site_domain()
            self.fields['password1'].required = False
            self.fields['password1'].widget = forms.HiddenInput()
            self.fields['password2'].required = False
            self.fields['password2'].widget = forms.HiddenInput()
        else:
            self.fields['password'].widget = forms.HiddenInput()
            self.fields['password1'].help_text = _("Suggestion: %s") % random_ascii(10)
            site_domain = self.plugin.site_domain
        if site_domain:
            site_link = '<a href="http://%s">%s</a>' % (site_domain, site_domain)
        else:
            site_link = '&lt;site_name&gt;.%s' % self.plugin.site_base_domain
        self.fields['site_url'].initial = site_link
        self.fields['name'].label = _("Username")
    
    def clean_password2(self):
        if not self.is_change:
            password1 = self.cleaned_data.get("password1")
            password2 = self.cleaned_data.get("password2")
            if password1 and password2 and password1 != password2:
                msg = _("The two password fields didn't match.")
                raise forms.ValidationError(msg)
            return password2
    
    def save(self, commit=True):
        obj = super(SoftwareServiceForm, self).save(commit=commit)
        if not self.is_change:
            obj.set_password(self.cleaned_data["password1"])
        return obj


class SoftwareService(plugins.Plugin):
    form = SoftwareServiceForm
    site_domain = None
    site_base_domain = None
    has_custom_domain = False
    icon = 'orchestra/icons/apps.png'
    class_verbose_name = _("Software as a Service")
    plugin_field = 'service'
    
    @classmethod
    @cached
    def get_plugins(cls):
        plugins = []
        for cls in settings.SAAS_ENABLED_SERVICES:
            plugins.append(import_class(cls))
        return plugins
    
    def get_change_readonly_fileds(cls):
        fields = super(SoftwareService, cls).get_change_readonly_fileds()
        return fields + ('name',)
    
    def get_site_domain(self):
        return self.site_domain or '.'.join(
            (self.instance.name, self.site_base_domain)
        )
    
    def clean_data(self):
        data = super(SoftwareService, self).clean_data()
        if not self.instance.pk:
            try:
                log = Operation.execute_action(self.instance, 'validate_creation')[0]
            except IndexError:
                pass
            else:
                if log.state != log.SUCCESS:
                    raise ValidationError(_("Validate creation execution has failed."))
                errors = {}
                if 'user-exists' in log.stdout:
                    errors['name'] = _("User with this username already exists.")
                if 'email-exists' in log.stdout:
                    errors['email'] = _("User with this email address already exists.")
                if errors:
                    raise ValidationError(errors)
        return data
    
    def save(self):
        pass
    
    def delete(self):
        pass
    
    def get_related(self):
        return []
