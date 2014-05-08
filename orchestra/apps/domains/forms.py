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
                Account = self.fields['account']._queryset.model
                cleaned_data['account'] = Account()
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


class DomainIterator(forms.models.ModelChoiceIterator):
    """ Group ticket owner by superusers, ticket.group and regular users """
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        self.domains = kwargs.pop('domains')
        super(forms.models.ModelChoiceIterator, self).__init__(*args, **kwargs)

    def __iter__(self):
        yield ('', '---------')
        account_domains = self.domains.filter(account=self.account)
        account_domains = account_domains.values_list('pk', 'name')
        yield (_("Account"), list(account_domains))
        domains = self.domains.exclude(account=self.account)
        domains = domains.values_list('pk', 'name')
        yield (_("Other"), list(domains))
