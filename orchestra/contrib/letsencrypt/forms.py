from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ungettext, ugettext_lazy as _

from .helpers import is_valid_domain


class LetsEncryptForm(forms.Form):
    domains = forms.CharField(widget=forms.Textarea)
    
    def __init__(self, domains, wildcards, *args, **kwargs):
        self.domains = domains
        self.wildcards = wildcards
        super().__init__(*args, **kwargs)
        if wildcards:
            help_text = _("You can add domains maching the following wildcards: %s")
            self.fields['domains'].help_text += help_text % ', '.join(wildcards)
    
    def clean_domains(self):
        domains = self.cleaned_data['domains'].split()
        cleaned_domains = set()
        for domain in domains:
            domain = domain.strip()
            if domain not in self.domains:
                domain = domain.strip()
                if not is_valid_domain(domain, self.domains, self.wildcards):
                    raise ValidationError(_(
                        "%s domain is not included on selected websites, "
                        "nor matches with any wildcard domain.") % domain
                    )
            cleaned_domains.add(domain)
        return cleaned_domains
