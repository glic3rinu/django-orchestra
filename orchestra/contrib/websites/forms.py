from django import forms
from django.core.exceptions import ValidationError
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

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
    """ Validate uniqueness """
    def clean(self):
        values = {}
        for form in self.forms:
            name = form.cleaned_data.get('name', None)
            if name is not None:
                directive = form.instance.directive_class
                if directive.unique_name and name in values:
                    form.add_error(None, ValidationError(
                        _("Only one %s can be defined.") % directive.get_verbose_name()
                    ))
                value = form.cleaned_data.get('value', None)
                if value is not None:
                    if directive.unique_value and value in values.get(name, []):
                        form.add_error('value', ValidationError(
                            _("This value is already used by other %s.") % force_text(directive.get_verbose_name())
                        ))
                try:
                    values[name].append(value)
                except KeyError:
                    values[name] = [value]
