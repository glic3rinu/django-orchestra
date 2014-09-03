from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
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
                    create_new_open=form.cleaned_data['create_new_open'],
                )
                return self.select_related(request)
        self.context.update({
            'title': _("Options for billing selected orders, step 1 / 3"),
            'step': 'one',
            'form': form,
        })
        return render(request, self.template, self.context)
    
    def select_related(self, request):
        self.options['related_queryset'] = self.queryset.all() #get_related(**options)
        form = BillSelectRelatedForm(initial=self.options)
        if request.POST.get('step') == 'two':
            form = BillSelectRelatedForm(request.POST, initial=self.options)
            if form.is_valid():
                select_related = form.cleaned_data['selected_related']
                self.options['selected_related'] = select_related
                return self.confirmation(request)
        self.context.update({
            'title': _("Select related order for billing, step 2 / 3"),
            'step': 'two',
            'form': form,
        })
        return render(request, self.template, self.context)
    
    def confirmation(self, request):
        form = BillSelectConfirmationForm(initial=self.options)
        if request.POST:
            bills = self.queryset.bill(commit=True, **self.options)
            if not bills:
                msg = _("Selected orders do not have pending billing")
                self.modeladmin.message_user(request, msg, messages.WARNING)
            else:
                ids = ','.join([str(bill.id) for bill in bills])
                url = reverse('admin:bills_bill_changelist')
                context = {
                    'url': url + '?id=%s' % ids,
                    'num': len(bills),
                    'bills': _("bills"),
                    'msg': _("have been generated"),
                }
                msg = '<a href="%(url)s">%(num)s %(bills)s</a> %(msg)s' % context
                msg = mark_safe(msg)
                self.modeladmin.message_user(request, msg, messages.INFO)
            return
        self.context.update({
            'title': _("Confirmation for billing selected orders"),
            'step': 'three',
            'form': form,
        })
        return render(request, self.template, self.context)
