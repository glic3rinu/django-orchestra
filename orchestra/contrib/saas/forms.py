from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import change_url
from orchestra.core import validators
from orchestra.forms.widgets import SpanWidget
from orchestra.plugins.forms import PluginDataForm
from orchestra.utils.python import random_ascii


class SaaSBaseForm(PluginDataForm):
    site_url = forms.CharField(label=_("Site URL"), widget=SpanWidget(), required=False)
    
    class Meta:
        exclude = ('database',)
        readonly_fields = ('site_url',)
    
    def __init__(self, *args, **kwargs):
        super(SaaSBaseForm, self).__init__(*args, **kwargs)
        self.is_change = bool(self.instance and self.instance.pk)
        if self.is_change:
            site_domain = self.instance.get_site_domain()
            if self.instance.custom_url:
                try:
                    website = self.instance.service_instance.get_website()
                except ObjectDoesNotExist:
                    link = ('<br><span style="color:red"><b>Warning:</b> '
                            'Related website directive does not exist for %s URL !</span>' % 
                            self.instance.custom_url)
                else:
                    url = change_url(website)
                    link = '<br>Related website: <a href="%s">%s</a>' % (url, website.name)
                self.fields['custom_url'].help_text += link
        else:
            site_domain = self.plugin.site_domain
        context = {
            'site_name': '&lt;site_name&gt;',
            'name': '&lt;site_name&gt;',
        }
        site_domain = site_domain % context
        if '&lt;site_name&gt;' in site_domain:
            site_link = site_domain
        else:
            site_link = '<a href="http://%s">%s</a>' % (site_domain, site_domain)
        self.fields['site_url'].widget.display = site_link
        self.fields['name'].label = _("Site name") if '%(' in self.plugin.site_domain else _("Username")


class SaaSPasswordForm(SaaSBaseForm):
    password = forms.CharField(label=_("Password"), required=False,
        widget=SpanWidget(display='<strong>Unknown password</strong>'),
        validators=[
            validators.validate_password,
            RegexValidator(r'^[^"\'\\]+$',
                           _('Enter a valid password. '
                             'This value may contain any ascii character except for '
                             ' \'/"/\\/ characters.'), 'invalid'),
        ],
        help_text=_("Passwords are not stored, so there is no way to see this "
                    "service's password, but you can change the password using "
                    "<a href=\"../password/\">this form</a>."))
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'off'}),
        validators=[validators.validate_password])
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))
    
    def __init__(self, *args, **kwargs):
        super(SaaSPasswordForm, self).__init__(*args, **kwargs)
        if self.is_change:
            self.fields['password1'].required = False
            self.fields['password1'].widget = forms.HiddenInput()
            self.fields['password2'].required = False
            self.fields['password2'].widget = forms.HiddenInput()
        else:
            self.fields['password'].widget = forms.HiddenInput()
            self.fields['password1'].help_text = _("Suggestion: %s") % random_ascii(10)
    
    def clean_password2(self):
        if not self.is_change:
            password1 = self.cleaned_data.get("password1")
            password2 = self.cleaned_data.get("password2")
            if password1 and password2 and password1 != password2:
                msg = _("The two password fields didn't match.")
                raise forms.ValidationError(msg)
            return password2
    
    def save(self, commit=True):
        obj = super(SaaSPasswordForm, self).save(commit=commit)
        if not self.is_change:
            obj.set_password(self.cleaned_data["password1"])
        return obj
