from billing import settings as billing_settings
from common.forms import FormAdminDjango
from common.widgets import CheckboxSelectMultipleTable
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from datetime import datetime
from itertools import chain
from models import ServiceAccounting
import settings


# Get all contenttypes whose models have 'CONTANT_FIELD attr'
contenttypes = []
for contenttype in ContentType.objects.all():
    if hasattr(contenttype.model_class(), settings.CONTACT_FIELD):
        contenttypes.append(contenttype.pk)


class ServiceAccountingAdminForm(forms.ModelForm):
    expression = forms.CharField(label='Expression', widget=forms.widgets.TextInput(attrs={'size':'150'}))
    billing_point = forms.ChoiceField(widget=forms.RadioSelect, 
        choices=settings.POINT_CHOICES, 
        initial=settings.DEFAULT_BILLING_POINT)
    pricing_point = forms.ChoiceField(widget=forms.RadioSelect, 
        choices=settings.POINT_CHOICES, 
        initial=settings.DEFAULT_PRICING_POINT)
    payment = forms.ChoiceField(widget=forms.RadioSelect, 
        choices=settings.PAYMENT_CHOICES, 
        initial=settings.DEFAULT_PAYMENT)
    pricing_with = forms.ChoiceField(widget=forms.RadioSelect, 
        choices=settings.PRICING_WITH_CHOICES, 
        initial=settings.DEFAULT_PRICING_WITH)
    pricing_effect = forms.ChoiceField(widget=forms.RadioSelect, 
        choices=settings.PRICING_EFFECT_CHOICES,
        initial=settings.DEFAULT_PRICING_EFFECT)
    weight_with = forms.ChoiceField(widget=forms.RadioSelect, 
        choices=settings.WEIGHT_WITH_CHOICES, 
        initial=settings.DEFAULT_WEIGHT_WITH)
    orders_with = forms.ChoiceField(widget=forms.RadioSelect, 
        choices=settings.ORDERS_WITH_CHOICES,
        initial=settings.DEFAULT_ORDERS_WITH)
        
    class Meta:
        model = ServiceAccounting
    
    def __init__(self, *args, **kwargs):
        super(ServiceAccountingAdminForm, self).__init__(*args, **kwargs)
        self.fields['content_type'].queryset = ContentType.objects.filter(pk__in=contenttypes)


class BillingOptions(forms.Form, FormAdminDjango):
    bill_point = forms.DateField(initial=datetime.now, widget=AdminDateWidget)
    fixed_point = forms.BooleanField(initial=billing_settings.DEFAULT_FIXED_POINT, required=False)
    force_next = forms.BooleanField(initial=billing_settings.DEFAULT_FORCE_NEXT, required=False)
    create_new_open = forms.BooleanField(initial=billing_settings.DEFAULT_CREATE_NEW_OPEN, required=False)


class NonSelectedDepsForm(forms.Form):
    """ This form is used to store not_selected_dependencies during formWizard transision """
    non_selected_deps = forms.CharField(widget=forms.HiddenInput(), required=False)    


def ListForm_Factory(qset, modeladmin, deps=None, req_post=None, initial=None):
    class ListForm(forms.Form):
        EFFECT_CHOICES = (
            ('B', 'Bill this ordres too'),
            ('O', 'Only use for Pricing'),)
        
        effect = forms.ChoiceField(choices=EFFECT_CHOICES, 
            initial=billing_settings.DEFAULT_EFFECT, required=True) 
        dependencies = forms.ModelMultipleChoiceField(
            widget=CheckboxSelectMultipleTable(modeladmin, dep_structure=deps), 
            queryset=qset, required=False)
        
        bill_point = forms.DateField(widget=forms.HiddenInput())
        fixed_point = forms.BooleanField(widget=forms.HiddenInput(), required=False)
        force_next = forms.BooleanField(widget=forms.HiddenInput(), required=False)
        create_new_open = forms.BooleanField(widget=forms.HiddenInput(), required=False)
        non_selected_deps = forms.CharField(widget=forms.HiddenInput(), required=False)    
        
    if req_post: return ListForm(req_post)
    if initial: return ListForm(initial=initial)
    return ListForm       


class ConfirmBillForm(forms.Form):
        dependencies = forms.CharField(widget=forms.HiddenInput(), required=False)
        bill_point = forms.DateField(widget=forms.HiddenInput())
        fixed_point = forms.BooleanField(widget=forms.HiddenInput(), required=False)
        force_next = forms.BooleanField(widget=forms.HiddenInput(), required=False)
        create_new_open = forms.BooleanField(widget=forms.HiddenInput(), required=False)
