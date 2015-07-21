from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.forms import AdminFormSet, AdminFormMixin

from . import validators
from .helpers import domain_for_validation
from .models import Domain


class BatchDomainCreationAdminForm(forms.ModelForm):
    name = forms.CharField(label=_("Names"), widget=forms.Textarea(attrs={'rows': 5, 'cols': 50}),
        help_text=_("Fully qualified domain name per line. "
                    "All domains will have the provided account and records."))
    
    def clean_name(self):
        self.extra_names = []
        target = None
        existing = set(Domain.objects.values_list('name', flat=True))
        errors = []
        for name in self.cleaned_data['name'].strip().splitlines():
            name = name.strip()
            if not name:
                continue
            if name in existing:
                 errors.append(ValidationError(_("%s domain name already exists.") % name))
            existing.add(name)
            if target is None:
                target = name
            else:
                domain = Domain(name=name)
                try:
                    domain.full_clean(exclude=['top'])
                except ValidationError as e:
                    raise ValidationError(e.error_dict['name'])
                self.extra_names.append(name)
        if errors:
            raise ValidationError(errors)
        return target
    
    def clean(self):
        """ inherit related parent domain account, when exists """
        cleaned_data = super(BatchDomainCreationAdminForm, self).clean()
        if not cleaned_data['account']:
            account = None
            for name in [cleaned_data['name']] + self.extra_names:
                parent = Domain.get_parent_domain(name)
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


class RecordForm(forms.ModelForm):
    class Meta:
        fields = ('ttl', 'type', 'value')
    
    def __init__(self, *args, **kwargs):
        super(RecordForm, self).__init__(*args, **kwargs)
        self.fields['ttl'].widget = forms.TextInput(attrs={'size': '10'})
        self.fields['value'].widget = forms.TextInput(attrs={'size': '100'})


class ValidateZoneMixin(object):
    def clean(self):
        """ Checks if everything is consistent """
        super(ValidateZoneMixin, self).clean()
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


class RecordEditFormSet(ValidateZoneMixin, AdminFormSet):
    pass


class RecordInlineFormSet(ValidateZoneMixin, forms.models.BaseInlineFormSet):
    pass


class SOAForm(AdminFormMixin, forms.Form):
    refresh = forms.CharField()
    clear_refresh = forms.BooleanField(label=_("Clear refresh"), required=False,
        help_text=_("Remove custom refresh value for all selected domains."))
    retry = forms.CharField()
    clear_retry = forms.BooleanField(label=_("Clear retry"), required=False,
        help_text=_("Remove custom retry value for all selected domains."))
    expire = forms.CharField()
    clear_expire = forms.BooleanField(label=_("Clear expire"), required=False,
        help_text=_("Remove custom expire value for all selected domains."))
    min_ttl = forms.CharField()
    clear_min_ttl = forms.BooleanField(label=_("Clear min TTL"), required=False,
        help_text=_("Remove custom min TTL value for all selected domains."))
    
    def __init__(self, *args, **kwargs):
        super(SOAForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            if not name.startswith('clear_'):
                field = Domain._meta.get_field_by_name(name)[0]
                self.fields[name] = forms.CharField(
                    label=capfirst(field.verbose_name),
                    help_text=field.help_text,
                    validators=field.validators,
                    required=False,
                )
