from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.forms import AdminFormMixin

from .models import Order


class BillSelectedOptionsForm(AdminFormMixin, forms.Form):
    billing_point = forms.DateField(initial=timezone.now,
            label=_("Billing point"),
            help_text=_("Date you want to bill selected orders"))
    fixed_point = forms.BooleanField(initial=False, required=False,
            label=_("fixed point"),
            help_text=_("Deisgnates whether you want the billing point to be an "
                        "exact date, or adapt it to the billing period."))
    create_new_open = forms.BooleanField(initial=False, required=False,
            label=_("Create a new open bill"),
            help_text=_("Deisgnates whether you want to put this orders on a new "
                        "open bill, or allow to reuse an existing one."))


class BillSelectRelatedForm(AdminFormMixin, forms.Form):
    selected_related = forms.ModelMultipleChoiceField(queryset=Order.objects.none(),
            required=False)
    billing_point = forms.DateField(widget=forms.HiddenInput())
    fixed_point = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    create_new_open = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    
    def __init__(self, *args, **kwargs):
        super(BillSelectRelatedForm, self).__init__(*args, **kwargs)
        queryset = kwargs['initial'].get('related_queryset', None)
        if queryset:
            self.fields['selected_related'].queryset = queryset


class BillSelectConfirmationForm(forms.Form):
    selected_related = forms.ModelMultipleChoiceField(queryset=Order.objects.none(),
            widget=forms.HiddenInput(), required=False)
    billing_point = forms.DateField(widget=forms.HiddenInput())
    fixed_point = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    create_new_open = forms.BooleanField(widget=forms.HiddenInput(), required=False)
