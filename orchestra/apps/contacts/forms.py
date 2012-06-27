from common.forms import FormAdminDjango
from django import forms
from django.utils.translation import ugettext as _


class MailForm(forms.Form, FormAdminDjango):
    mail_from = forms.CharField(widget=forms.TextInput(attrs={'size': 128,}), max_length=128, required=True)
    subject = forms.CharField(widget=forms.TextInput(attrs={'size': 128,}), max_length=256, required=True)
    body = forms.CharField(widget=forms.widgets.Textarea(attrs={'cols':92,}), required=True)

