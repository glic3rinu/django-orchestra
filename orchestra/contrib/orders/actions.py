from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext, ugettext_lazy as _
from django.shortcuts import render

from orchestra.admin.utils import change_url

from .forms import BillSelectedOptionsForm, BillSelectConfirmationForm, BillSelectRelatedForm


class BillSelectedOrders(object):
    """ Form wizard for billing orders admin action """
    short_description = _("Bill selected orders")
    verbose_name = _("Bill")
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
                    proforma=form.cleaned_data['proforma'],
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
                self.modeladmin.log_change(request, order, _("Billed"))
            if not bills:
                msg = _("Selected orders do not have pending billing")
                self.modeladmin.message_user(request, msg, messages.WARNING)
            else:
                num = len(bills)
                if num == 1:
                    url = change_url(bills[0])
                else:
                    url = reverse('admin:bills_bill_changelist')
                    ids = ','.join(map(str, bills))
                    url += '?id__in=%s' % ids
                msg = ungettext(
                    '<a href="{url}">One bill</a> has been created.',
                    '<a href="{url}">{num} bills</a> have been created.',
                    num).format(url=url, num=num)
                msg = mark_safe(msg)
                self.modeladmin.message_user(request, msg, messages.INFO)
            return
        bills = self.queryset.bill(commit=False, **self.options)
        bills_with_total = []
        for account, lines in bills:
            total = 0
            for line in lines:
                discount = sum([discount.total for discount in line.discounts])
                total += line.subtotal + discount
            bills_with_total.append((account, total, lines))
        self.context.update({
            'title': _("Confirmation for billing selected orders"),
            'step': 3,
            'form': form,
            'bills': bills_with_total,
        })
        return render(request, self.template, self.context)


@transaction.atomic
def mark_as_ignored(modeladmin, request, queryset):
    """ Mark orders as ignored """
    for order in queryset:
        order.mark_as_ignored()
        modeladmin.log_change(request, order, 'Marked as ignored')
    num = len(queryset)
    msg = ungettext(
        _("Selected order has been marked as ignored."),
        _("%i selected orders have been marked as ignored.") % num,
        num)
    modeladmin.message_user(request, msg)


@transaction.atomic
def mark_as_not_ignored(modeladmin, request, queryset):
    """ Mark orders as ignored """
    for order in queryset:
        order.mark_as_not_ignored()
        modeladmin.log_change(request, order, 'Marked as not ignored')
    num = len(queryset)
    msg = ungettext(
        _("Selected order has been marked as not ignored."),
        _("%i selected orders have been marked as not ignored.") % num,
        num)
    modeladmin.message_user(request, msg)

