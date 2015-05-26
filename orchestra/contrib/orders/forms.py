from django import forms
from django.contrib.admin import widgets
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.forms import AdminFormMixin
from orchestra.admin.utils import change_url

from .models import Order


class BillSelectedOptionsForm(AdminFormMixin, forms.Form):
    billing_point = forms.DateField(initial=timezone.now,
        label=_("Billing point"), widget=widgets.AdminDateWidget,
        help_text=_("Date you want to bill selected orders"))
    fixed_point = forms.BooleanField(initial=False, required=False,
        label=_("Fixed point"),
        help_text=_("Deisgnates whether you want the billing point to be an "
                    "exact date, or adapt it to the billing period."))
    proforma = forms.BooleanField(initial=False, required=False,
        label=_("Pro-forma (billing simulation)"),
        help_text=_("Creates a Pro Forma instead of billing the orders."))
    new_open = forms.BooleanField(initial=False, required=False,
        label=_("Create a new open bill"),
        help_text=_("Deisgnates whether you want to put this orders on a new "
                    "open bill, or allow to reuse an existing one."))


def selected_related_choices(queryset):
    for order in queryset:
        verbose = '<a href="{order_url}">{description}</a> '
        verbose += '<a class="account" href="{account_url}">{account}</a>'
        if order.ignore:
            verbose += ' (ignored)'
        verbose = verbose.format(
            order_url=change_url(order), description=order.description,
            account_url=change_url(order.account), account=str(order.account)
        )
        yield (order.pk, mark_safe(verbose))


class BillSelectRelatedForm(AdminFormMixin, forms.Form):
     # This doesn't work well with reordering after billing
#    pricing_with_all = forms.BooleanField(label=_("Do pricing with all orders"),
#            initial=False, required=False, help_text=_("The price may vary "
#                "depending on the billed orders. This options designates whether "
#                "all existing orders will be used for price computation or not."))
    select_all = forms.BooleanField(label=_("Select all"), required=False)
    selected_related = forms.ModelMultipleChoiceField(label=_("Related orders"),
        queryset=Order.objects.none(), widget=forms.CheckboxSelectMultiple,
        required=False)
    billing_point = forms.DateField(widget=forms.HiddenInput())
    fixed_point = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    proforma = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    new_open = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    
    def __init__(self, *args, **kwargs):
        super(BillSelectRelatedForm, self).__init__(*args, **kwargs)
        queryset = kwargs['initial'].get('related_queryset', None)
        if queryset:
            self.fields['selected_related'].queryset = queryset
        self.fields['selected_related'].choices = selected_related_choices(queryset)


class BillSelectConfirmationForm(AdminFormMixin, forms.Form):
    billing_point = forms.DateField(widget=forms.HiddenInput())
    fixed_point = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    proforma = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    new_open = forms.BooleanField(widget=forms.HiddenInput(), required=False)
