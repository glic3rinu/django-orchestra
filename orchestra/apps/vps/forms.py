from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _


class VPSCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))
    
    class Meta:
        fields = ('username', 'account', 'type', 'template')
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            msg = _("The two password fields didn't match.")
            raise forms.ValidationError(msg)
        return password2
    
    def save(self, commit=True):
        vps = super(VPSCreationForm, self).save(commit=False)
        vps.set_password(self.cleaned_data["password1"])
        if commit:
            vps.save()
        return vps


class VPSChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))
    
    def clean_password(self):
        return self.initial["password"]
