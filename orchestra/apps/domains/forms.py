from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from . import validators
from .helpers import domain_for_validation
from .models import Domain


class DomainAdminForm(forms.ModelForm):
    def clean(self):
        """ inherit related top domain account, when exists """
        cleaned_data = super(DomainAdminForm, self).clean()
        if not cleaned_data['account']:
            domain = Domain(name=cleaned_data['name'])
            top = domain.get_top()
            if not top:
                # Fake an account to make django validation happy
                account_model = self.fields['account']._queryset.model
                cleaned_data['account'] = account_model()
                msg = _("An account should be provided for top domain names")
                raise ValidationError(msg)
            cleaned_data['account'] = top.account
        return cleaned_data


class RecordInlineFormSet(forms.models.BaseInlineFormSet):
    def clean(self):
        """ Checks if everything is consistent """
        if any(self.errors):
            return
        if self.instance.name:
            records = []
            for form in self.forms:
                data = form.cleaned_data
                if data and not data['DELETE']:
                    records.append(data)
            domain = domain_for_validation(self.instance, records)
            validators.validate_zone(domain.render_zone())
