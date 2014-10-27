from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from . import validators
from .helpers import domain_for_validation
from .models import Domain


class CreateDomainAdminForm(forms.ModelForm):
#    migrate_subdomains = forms.BooleanField(label=_("Migrate subdomains"), required=False,
#            initial=False, help_text=_("Propagate the account owner change to subdomains."))
    
    def clean(self):
        """ inherit related top domain account, when exists """
        cleaned_data = super(CreateDomainAdminForm, self).clean()
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


#class BatchDomainCreationAdminForm(DomainAdminForm):
#    # TODO
#    name = forms.CharField(widget=forms.Textarea, label=_("Names"),
#            help_text=_("Domain per line. All domains will share the same attributes."))
#    
#    def clean_name(self):
#        self.names = []
#        target = None
#        for name in self.cleaned_data['name'].splitlines():
#            name = name.strip()
#            if target is None:
#                target = name
#            else:
#                domain = Domain(name=name)
#                try:
#                    domain.full_clean(exclude=['top'])
#                except ValidationError as e:
#                    raise ValidationError(e.error_dict['name'])
#                self.names.append(name)
#        return target
#    
#    def save_model(self, request, obj, form, change):
#        # TODO thsi is modeladmin
#        """ batch domain creation support """
#        super(DomainAdmin, self).save_model(request, obj, form, change)
#        if not change:
#            for name in form.names:
#                domain = Domain.objects.create(name=name, account_id=obj.account_id)
#    
#    def save_related(self, request, form, formsets, change):
#        # TODO thsi is modeladmin
#        """ batch domain creation support """
#        super(DomainAdmin, self).save_related(request, form, formsets, change)
#        if not change:
#            for name in form.names:
#                for formset in formsets:
#                    formset.instance = form.instance
#                    self.save_formset(request, form, formset, change=change)


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
