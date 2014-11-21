from django import forms
from django.core import validators
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.forms.widgets import ShowTextWidget

from . import settings


class SendEmailForm(forms.Form):
    email_from = forms.EmailField(label=_("From"),
            initial=settings.CONTACTS_DEFAULT_FROM_EMAIL,
            widget=forms.TextInput(attrs={'size':'118'}))
    cc = forms.CharField(label="CC", required=False,
            widget=forms.TextInput(attrs={'size':'118'}))
    bcc = forms.CharField(label="BCC", required=False,
            widget=forms.TextInput(attrs={'size':'118'}))
    subject = forms.CharField(label=_("Subject"),
            widget=forms.TextInput(attrs={'size':'118'}))
    message = forms.CharField(label=_("Message"),
            widget=forms.Textarea(attrs={'cols': 118, 'rows': 15}))
    
    def clean_space_separated_emails(self, value):
        value = value.split()
        for email in value:
            try:
                validators.validate_email(email)
            except validators.ValidationError:
                raise validators.ValidationError("Space separated emails.")
        return value
    
    def clean_cc(self):
        return self.clean_space_separated_emails(self.cleaned_data['cc'])
    
    def clean_bcc(self):
        return self.clean_space_separated_emails(self.cleaned_data['bcc'])
