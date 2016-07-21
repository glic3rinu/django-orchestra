from collections import defaultdict

from django import forms
from django.core.exceptions import ValidationError

from .utils import normurlpath
from .validators import validate_domain_protocol, validate_server_name


class WebsiteAdminForm(forms.ModelForm):
    def clean(self):
        """ Prevent multiples domains on the same protocol """
        super(WebsiteAdminForm, self).clean()
        domains = self.cleaned_data.get('domains')
        if not domains:
            return self.cleaned_data
        protocol = self.cleaned_data.get('protocol')
        domains = domains.all()
        for domain in domains:
            try:
                validate_domain_protocol(self.instance, domain, protocol)
            except ValidationError as err:
                self.add_error(None, err)
        try:
            validate_server_name(domains)
        except ValidationError as err:
            self.add_error('domains', err)
        return self.cleaned_data


class WebsiteDirectiveInlineFormSet(forms.models.BaseInlineFormSet):
    def clean(self):
        # directives formset cross-validation with contents for unique locations
        locations = set()
        for form in self.content_formset.forms:
            location = form.cleaned_data.get('path')
            delete = form.cleaned_data.get('DELETE')
            if not delete and location is not None:
                locations.add(normurlpath(location))
        
        values = defaultdict(list)
        for form in self.forms:
            wdirective = form.instance
            directive = form.cleaned_data
            if directive.get('name') is not None:
                try:
                    wdirective.directive_instance.validate_uniqueness(directive, values, locations)
                except ValidationError as err:
                    for k,v in err.error_dict.items():
                        form.add_error(k, v)
