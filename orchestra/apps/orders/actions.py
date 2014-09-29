from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext
from django.shortcuts import render

from .forms import (BillSelectedOptionsForm, BillSelectConfirmationForm,
        BillSelectRelatedForm)


class BillSelectedOrders(object):
    """ Form wizard for billing orders admin action """
    short_description = _("Bill selected orders")
    template = 'admin/orders/order/bill_selected_options.html'
    __name__ = 'bill_selected_orders'
    
    def __call__(self, modeladmin, request, queryset):
        """ make this monster behave like a function """
        self.modeladmin = modeladmin
        self.queryset = queryset
        opts = modeladmin.model._meta
        app_label = opts.app_label
        self.context = {
            'opts': opts,
            'app_label': app_label,
            'queryset': queryset,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }
        return self.set_options(request)
    
    def set_options(self, request):
        form = BillSelectedOptionsForm()
        if request.POST.get('step'):
            form = BillSelectedOptionsForm(request.POST)
            if form.is_valid():
                self.options = dict(
                    billing_point=form.cleaned_data['billing_point'],
                    fixed_point=form.cleaned_data['fixed_point'],
                    is_proforma=form.cleaned_data['is_proforma'],
                    new_open=form.cleaned_data['new_open'],
                )
                if int(request.POST.get('step')) != 3:
                    return self.select_related(request)
                else:
                    return self.confirmation(request)
        self.context.update({
            'title': _("Options for billing selected orders, step 1 / 3"),
            'step': 1,
            'form': form,
        })
        return render(request, self.template, self.context)
    
    def select_related(self, request):
        # TODO use changelist ?
        related = self.queryset.get_related().select_related('account', 'service')
        if not related:
            return self.confirmation(request)
        self.options['related_queryset'] = related
        form = BillSelectRelatedForm(initial=self.options)
        if int(request.POST.get('step')) >= 2:
            form = BillSelectRelatedForm(request.POST, initial=self.options)
            if form.is_valid():
                select_related = form.cleaned_data['selected_related']
                self.queryset = self.queryset | select_related
                return self.confirmation(request)
        self.context.update({
            'title': _("Select related order for billing, step 2 / 3"),
            'step': 2,
            'form': form,
        })
        return render(request, self.template, self.context)
    
    @transaction.atomic
    def confirmation(self, request):
        form = BillSelectConfirmationForm(initial=self.options)
        if int(request.POST.get('step')) >= 3:
            bills = self.queryset.bill(commit=True, **self.options)
            for order in self.queryset:
                self.modeladmin.log_change(request, order, 'Billed')
            if not bills:
                msg = _("Selected orders do not have pending billing")
                self.modeladmin.message_user(request, msg, messages.WARNING)
            else:
                ids = ','.join([str(bill.id) for bill in bills])
                url = reverse('admin:bills_bill_changelist')
                url += '?id__in=%s' % ids
                num = len(bills)
                msg = ungettext(
                    '<a href="{url}">One bill</a> has been created.',
                    '<a href="{url}">{num} bills</a> have been created.',
                    num).format(url=url, num=num)
                msg = mark_safe(msg)
                self.modeladmin.message_user(request, msg, messages.INFO)
            return
        bills = self.queryset.bill(commit=False, **self.options)
        self.context.update({
            'title': _("Confirmation for billing selected orders"),
            'step': 3,
            'form': form,
            'bills': bills,
        })
        return render(request, self.template, self.context)
