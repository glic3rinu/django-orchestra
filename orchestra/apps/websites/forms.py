from django import forms
from django.core.exceptions import ValidationError

from .validators import validate_domain_protocol


class WebsiteAdminForm(forms.ModelForm):
    def clean(self):
        """ Prevent multiples domains on the same protocol """
        domains = self.cleaned_data.get('domains')
        if not domains:
            return self.cleaned_data
        protocol = self.cleaned_data.get('protocol')
        for domain in domains.all():
            try:
                validate_domain_protocol(self.instance, domain, protocol)
            except ValidationError as e:
                # TODO not sure about this one
                self.add_error(None, e)
        return self.cleaned_data

