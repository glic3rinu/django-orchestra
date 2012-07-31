from models import Order
from django.contrib import admin
from forms import ListForm_Factory, BillingOptions, ConfirmBillForm, NonSelectedDepsForm
from django import forms
from django.shortcuts import render_to_response
from django import template
from helpers import get_billing_dependencies
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from datetime import datetime

def billing_options_view(modeladmin, request, queryset):

    opts = modeladmin.model._meta
    app_label = opts.app_label
    if request.POST.get('post') == 'billing_options':
        form = BillingOptions(request.POST)
        if form.is_valid():
            bill_point = form.cleaned_data['bill_point']
            fixed_point = form.cleaned_data['fixed_point']
            force_next = form.cleaned_data['force_next']
            create_new_open = form.cleaned_data['create_new_open']
            not_selected_dependencies = get_billing_dependencies(queryset,
                                        exclude=queryset.values_list('pk', flat=True), fixed_point=fixed_point,
                                        point=datetime(*bill_point.timetuple()[:6]), force_next=force_next)
            if not not_selected_dependencies:
                return confirm_bill_view(modeladmin, request, queryset, 
                        bill_point, fixed_point, force_next, create_new_open)
            return select_dependencies_view(modeladmin, request, queryset, 
                not_selected_dependencies, bill_point, fixed_point, force_next, create_new_open)
    elif request.POST.get('post') == 'select_dependencies':
        form = NonSelectedDepsForm(request.POST)
        if form.is_valid():
            non_selected_deps = form.cleaned_data['non_selected_deps']
        not_selected_dependencies = list(non_selected_deps.split(',')) if non_selected_deps else []
        not_selected_qset = Order.objects.filter(pk__in=not_selected_dependencies)
        return select_dependencies_view(modeladmin, request, queryset, not_selected_dependencies=not_selected_qset)
    elif request.POST.get('post') == 'confirm_bill':
        return confirm_bill_view(modeladmin, request, queryset)
              
    form = BillingOptions()
                    
    context = {
        "title": 'Billing Options',
        "form": form,
        "opts": opts,
        "app_label": app_label,
        "queryset": queryset,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
    }
    return render_to_response("admin/ordering/order/billing_options.html", context, 
                              context_instance=template.RequestContext(request))



def select_dependencies_view(modeladmin, request, queryset, not_selected_dependencies={}, 
                             bill_point=None, fixed_point=None, force_next=None, create_new_open=None):

    if isinstance(not_selected_dependencies, dict):
        pks = [ order.pk for order in not_selected_dependencies ]
        qset = Order.objects.filter(pk__in=pks)
    else: qset = not_selected_dependencies

    if request.POST.get('post') == 'select_dependencies':        
        # deal with chosen items
        form = ListForm_Factory(qset, modeladmin, req_post=request.POST)
        if form.is_valid():
            bill_point = form.cleaned_data['bill_point']
            fixed_point = form.cleaned_data['fixed_point']
            force_next = form.cleaned_data['force_next']
            create_new_open = form.cleaned_data['create_new_open']
            effect = form.cleaned_data['effect']
            chosen_qset = form.cleaned_data['dependencies']
            if effect == 'B': b_qset = set(queryset).union(set(chosen_qset))
            else: b_qset = queryset
            return confirm_bill_view(modeladmin, request, b_qset, bill_point, fixed_point, 
                                     force_next, create_new_open, dependencies=chosen_qset )

    #deal with a GET request
    deps = ','.join([str(i) for i in qset.values_list('pk', flat=True)]) if qset else ''
    initial = { 'bill_point': bill_point, 
                'fixed_point': fixed_point,
                'force_next': force_next,
                'create_new_open': create_new_open,
                'non_selected_deps': deps }

    form = ListForm_Factory(qset, modeladmin, deps=not_selected_dependencies, initial = initial)
    print form
    opts = modeladmin.model._meta
    app_label = opts.app_label

    context = {
        "title": 'Pricing Dependencies slection',
        "form": form,
        "opts": opts,
        "app_label": app_label,
        "queryset": queryset,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME, }
        
    return render_to_response("admin/ordering/order/select_dependencies.html", context, 
            context_instance=template.RequestContext(request))
    
    
    
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

def confirm_bill_view(modeladmin, request, queryset, bill_point=None, fixed_point=None, 
                        force_next=None, create_new_open=None, dependencies=None):
    opts = modeladmin.model._meta
    app_label = opts.app_label
    if request.POST.get('post') == 'confirm_bill':  
        form = ConfirmBillForm(request.POST)
        if form.is_valid():   
            dependencies = form.cleaned_data['dependencies']
            bill_point = datetime(*form.cleaned_data['bill_point'].timetuple()[:6])
            fixed_point = form.cleaned_data['fixed_point']
            force_next = form.cleaned_data['force_next']
            create_new_open = form.cleaned_data['create_new_open']
            
            dep_list = list(dependencies.split(',')) if dependencies else []
            deps_qset = Order.objects.filter(pk__in=dep_list)
            dep_list.extend(queryset.values_list('pk', flat=True))
            pricing_qset = Order.objects.filter(pk__in=dep_list)

            bills = Order.bill_orders(queryset, point=bill_point, pricing_orders=pricing_qset,
                              fixed_point=fixed_point, force_next=force_next, create_new_open=create_new_open, commit=True)
            if not bills:
                messages.add_message(request, messages.WARNING, _("This orders doesnt have any pending period beyond the point"))
            else:
                #TODO: pass a bill link inside a message.  
                messages.add_message(request, messages.INFO, _("Orders are succefully billed in %s bills" % len(bills)))
            return None
            
    deps = ','.join([str(i) for i in dependencies.values_list('pk', flat=True)]) if dependencies else ''
    initial = { 'bill_point': bill_point, 
                'fixed_point': fixed_point,
                'force_next': force_next,
                'create_new_open': create_new_open,
                'dependencies': deps }
                
    form = ConfirmBillForm(initial=initial)
      
    orders_to_bill = []
    for order in queryset:
        obj_url = reverse(('%s:ordering_order_change' % modeladmin.admin_site.name), args=(order.pk,))
        string = mark_safe(u'<a href="%s">%s(%s)</a>' % (obj_url, str(order), str(order.contract.content_object)))
        orders_to_bill.append(string)
      
    context = {
        "title": 'Billing Confirmation',
        "form": form,
        "opts": opts,
        'queryset': queryset,
        "orders_to_bill": orders_to_bill,
        "app_label": app_label,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME, }
        
    return render_to_response("admin/ordering/order/bill_selected_confirmation.html", 
            dict(context, **initial), context_instance=template.RequestContext(request))

