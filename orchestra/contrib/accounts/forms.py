import logging
from collections import OrderedDict

from django import forms
from django.core.exceptions import ValidationError
from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from orchestra.forms import UserCreationForm

from . import settings
from .models import Account


logger = logging.getLogger(__name__)


def create_account_creation_form():
    fields = OrderedDict(**{
        'enable_systemuser': forms.BooleanField(initial=True, required=False,
            label=_("Enable systemuser"),
            help_text=_("Designates whether to creates an enabled or disabled related system user. "
                        "Notice that a related system user will be always created."))
    })
    create_related = []
    for model, key, kwargs, help_text in settings.ACCOUNTS_CREATE_RELATED:
        try:
            model = apps.get_model(model)
        except LookupError:
            logger.error("%s not installed." % model)
        else:
            field_name = 'create_%s' % model._meta.model_name
            label = _("Create %s") % model._meta.verbose_name
            fields[field_name] = forms.BooleanField(
                initial=True, required=False, label=label, help_text=help_text)
            create_related.append((model, key, kwargs, help_text))
        
    def clean(self, create_related=create_related):
        """ unique usernames between accounts and system users """
        cleaned_data = UserCreationForm.clean(self)
        try:
            account = Account(
                username=cleaned_data['username'],
                password=cleaned_data['password1']
            )
        except KeyError:
            # Previous validation error
            return
        errors = {}
        systemuser_model = Account.main_systemuser.field.rel.to
        if systemuser_model.objects.filter(username=account.username).exists():
            errors['username'] = _("A system user with this name already exists.")
        for model, key, related_kwargs, __ in create_related:
            kwargs = {
                key: eval(related_kwargs[key], {'account': account})
            }
            if model.objects.filter(**kwargs).exists():
                verbose_name = model._meta.verbose_name
                field_name = 'create_%s' % model._meta.model_name
                errors[field_name] = ValidationError(
                    _("A %(type)s with this name already exists."),
                    params={'type': verbose_name})
        if errors:
            raise ValidationError(errors)
    
    def save_model(self, account):
        enable_systemuser=self.cleaned_data['enable_systemuser']
        account.save(active_systemuser=enable_systemuser)
    
    def save_related(self, account):
        for model, key, related_kwargs, __ in settings.ACCOUNTS_CREATE_RELATED:
            model = apps.get_model(model)
            field_name = 'create_%s' % model._meta.model_name
            if self.cleaned_data[field_name]:
                kwargs = {
                    key: eval(value, {'account': account}) for key, value in related_kwargs.items()
                }
                model.objects.create(account=account, **kwargs)
    
    fields.update({
        'create_related_fields': list(fields.keys()),
        'clean': clean,
        'save_model': save_model,
        'save_related': save_related,
    })
    
    return type('AccountCreationForm', (UserCreationForm,), fields)


AccountCreationForm = create_account_creation_form()
