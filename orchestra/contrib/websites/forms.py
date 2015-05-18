from collections import defaultdict

from django import forms
from django.core.exceptions import ValidationError
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from .directives import SiteDirective
from .validators import validate_domain_protocol


class WebsiteAdminForm(forms.ModelForm):
    def clean(self):
        """ Prevent multiples domains on the same protocol """
        super(WebsiteAdminForm, self).clean()
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


class WebsiteDirectiveInlineFormSet(forms.models.BaseInlineFormSet):
    def clean(self):
        # directives formset cross-validation with contents for unique locations
        locations = set()
        for form in self.content_formset.forms:
            location = form.cleaned_data.get('path')
            if location is not None:
                locations.add(location)
        directives = []
        
        values = defaultdict(list)
        for form in self.forms:
            website = form.instance
            directive = form.cleaned_data
            if directive.get('name') is not None:
                try:
                    website.directive_instance.validate_uniqueness(directive, values, locations)
                except ValidationError as err:
                    for k,v in err.error_dict.items():
                        form.add_error(k, v)
