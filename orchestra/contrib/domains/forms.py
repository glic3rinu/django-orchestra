from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.forms import AdminFormSet, AdminFormMixin

from . import validators
from .helpers import domain_for_validation
from .models import Domain, Record


class BatchDomainCreationAdminForm(forms.ModelForm):
    name = forms.CharField(label=_("Names"), widget=forms.Textarea(attrs={'rows': 5, 'cols': 50}),
        help_text=_("Fully qualified domain name per line. "
                    "All domains will have the provided account and records."))

    def clean_name(self):
        self.extra_names = []
        target = None
        existing = set()
        errors = []
        domain_names = self.cleaned_data['name'].strip().splitlines()
        for name in domain_names:
            name = name.strip()
            if not name:
                continue
            if name in existing:
                errors.append(ValidationError(_("%s domain name provided multiple times.") % name))
            existing.add(name)
            if target is None:
                target = name
            else:
                domain = Domain(name=name)
                try:
                    domain.full_clean(exclude=['top'])
                except ValidationError as e:
                    for error in e.error_dict['name']:
                        for msg in error.messages:
                            errors.append(
                                ValidationError("%s: %s" % (name, msg))
                            )
                self.extra_names.append(name)
        if errors:
            raise ValidationError(errors)
        return target
    
    def clean(self):
        """ inherit related parent domain account, when exists """
        cleaned_data = super().clean()
        if not cleaned_data['account']:
            account = None
            domain_names = []
            if 'name' in cleaned_data:
                first = cleaned_data['name']
                domain_names.append(first)
            domain_names.extend(self.extra_names)
            for name in domain_names:
                parent = Domain.objects.get_parent(name)
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
        
        def full_clean(self):
            # set extra_names on instance to use it on inline formsets validation
            super().full_clean()
            self.instance.extra_names = extra_names


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
        is_host = True
        for form in self.forms:
            if form.cleaned_data.get('type') in (Record.TXT, Record.SRV, Record.CNAME):
                is_host = False
                break
        domain_names = []
        if self.instance.name:
            domain_names.append(self.instance.name)
        domain_names.extend(getattr(self.instance, 'extra_names', []))
        errors = []
        for name in domain_names:
            records = []
            for form in self.forms:
                data = form.cleaned_data
                if data and not data['DELETE']:
                    records.append(data)
            if '_' in name and is_host:
                errors.append(ValidationError(
                    _("%s: Hosts can not have underscore character '_', consider providing a SRV, CNAME or TXT record.") % name
                ))
            domain = domain_for_validation(self.instance, records)
            try:
                validators.validate_zone(domain.render_zone())
            except ValidationError as error:
                for msg in error:
                    errors.append(
                        ValidationError("%s: %s" % (name, msg))
                    )
        if errors:
            raise ValidationError(errors)


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
                field = Domain._meta.get_field(name)
                self.fields[name] = forms.CharField(
                    label=capfirst(field.verbose_name),
                    help_text=field.help_text,
                    validators=field.validators,
                    required=False,
                )
