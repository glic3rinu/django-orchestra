from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from . import validators
from .helpers import domain_for_validation
from .models import Domain


class BatchDomainCreationAdminForm(forms.ModelForm):
    name = forms.CharField(label=_("Names"), widget=forms.Textarea(attrs={'rows': 5, 'cols': 50}),
        help_text=_("Domain per line. All domains will share the same attributes."))
    
    def clean_name(self):
        self.extra_names = []
        target = None
        for name in self.cleaned_data['name'].strip().splitlines():
            name = name.strip()
            if not name:
                continue
            if target is None:
                target = name
            else:
                domain = Domain(name=name)
                try:
                    domain.full_clean(exclude=['top'])
                except ValidationError as e:
                    raise ValidationError(e.error_dict['name'])
                self.extra_names.append(name)
        return target
    
    def clean(self):
        """ inherit related parent domain account, when exists """
        cleaned_data = super(BatchDomainCreationAdminForm, self).clean()
        if not cleaned_data['account']:
            account = None
            for name in [cleaned_data['name']] + self.extra_names:
                domain = Domain(name=name)
                parent = domain.get_parent()
                if not parent:
                    # Fake an account to make django validation happy
                    account_model = self.fields['account']._queryset.model
                    cleaned_data['account'] = account_model()
                    raise ValidationError({
                        'account': _("An account should be provided for top domain names."),
                    })
                elif account and parent.account != account:
                    # Fake an account to make django validation happy
                    account_model = self.fields['account']._queryset.model
                    cleaned_data['account'] = account_model()
                    raise ValidationError({
                        'account': _("Provided domain names belong to different accounts."),
                    })
                account = parent.account
                cleaned_data['account'] = account
        return cleaned_data


class RecordInlineFormSet(forms.models.BaseInlineFormSet):
    def clean(self):
        """ Checks if everything is consistent """
        super(RecordInlineFormSet, self).clean()
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
