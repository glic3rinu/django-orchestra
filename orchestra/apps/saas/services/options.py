from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra import plugins
from orchestra.plugins.forms import PluginDataForm
from orchestra.core import validators
from orchestra.forms import widgets
from orchestra.utils.functional import cached
from orchestra.utils.python import import_class

from .. import settings


class SoftwareServiceForm(PluginDataForm):
    site_name = forms.CharField(widget=widgets.ShowTextWidget, required=False)
    password = forms.CharField(label=_("Password"), required=False,
            widget=widgets.ReadOnlyWidget('<strong>Unknown password</strong>'),
            help_text=_("Passwords are not stored, so there is no way to see this "
                        "service's password, but you can change the password using "
                        "<a href=\"password/\">this form</a>."))
    password1 = forms.CharField(label=_("Password"), validators=[validators.validate_password],
            widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
            widget=forms.PasswordInput,
            help_text=_("Enter the same password as above, for verification."))
    
    def __init__(self, *args, **kwargs):
        super(SoftwareServiceForm, self).__init__(*args, **kwargs)
        self.is_change = bool(self.instance and self.instance.pk)
        if self.is_change:
            site_name = self.instance.get_site_name()
            self.fields['password1'].required = False
            self.fields['password1'].widget = forms.HiddenInput()
            self.fields['password2'].required = False
            self.fields['password2'].widget = forms.HiddenInput()
        else:
            self.fields['password'].widget = forms.HiddenInput()
            site_name = self.plugin.site_name
        if site_name:
            site_name_link = '<a href="http://%s">%s</a>' % (site_name, site_name)
        else:
            site_name_link = '&lt;name&gt;.%s' % self.plugin.site_name_base_domain
        self.fields['site_name'].initial = site_name_link
##            self.fields['site_name'].widget = widgets.ReadOnlyWidget(site_name, mark_safe(link))
##            self.fields['site_name'].required = False
#        else:
#            base_name = self.plugin.site_name_base_domain
#            help_text = _("The final URL would be &lt;site_name&gt;.%s") % base_name
#            self.fields['site_name'].help_text = help_text
    
    def clean_password2(self):
        if not self.is_change:
            password1 = self.cleaned_data.get("password1")
            password2 = self.cleaned_data.get("password2")
            if password1 and password2 and password1 != password2:
                msg = _("The two password fields didn't match.")
                raise forms.ValidationError(msg)
            return password2
    
    def clean_site_name(self):
        if self.plugin.site_name:
            return None
        return self.cleaned_data['site_name']
    
    def save(self, commit=True):
        obj = super(SoftwareServiceForm, self).save(commit=commit)
        if not self.is_change:
            obj.set_password(self.cleaned_data["password1"])
        return obj


class SoftwareService(plugins.Plugin):
    form = SoftwareServiceForm
    site_name = None
    site_name_base_domain = 'orchestra.lan'
    has_custom_domain = False
    icon = 'orchestra/icons/apps.png'
    change_readonly_fileds = ('site_name',)
    class_verbose_name = _("Software as a Service")
    plugin_field = 'service'
    
    @classmethod
    @cached
    def get_plugins(cls):
        plugins = []
        for cls in settings.SAAS_ENABLED_SERVICES:
            plugins.append(import_class(cls))
        return plugins
    
    @classmethod
    def get_change_readonly_fileds(cls):
        fields = super(SoftwareService, cls).get_change_readonly_fileds()
        return fields + ('username',)
    
    def get_site_name(self):
        return self.site_name or '.'.join(
            (self.instance.username, self.site_name_base_domain)
        )
    
    def save(self):
        pass
    
    def delete(self):
        pass
