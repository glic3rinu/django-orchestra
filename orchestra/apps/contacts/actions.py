

""" All the actions contained on this module are legacy crap and must be rewrited """


from django.contrib.admin.util import get_deleted_objects, NestedObjects
from common.utils.admin import get_modeladmin
from common.utils.python import lists_to_list
from common.utils.models import group_by
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.contrib import admin 
from django.shortcuts import render_to_response
from django import template
from django.contrib import messages
from contacts.models import Contract, Contact
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
#from common.models import Service
from django.db import router

#TODO delete this shit and deprecate all this functions
class Service(object):pass

def get_format_callback(opts, user, admin_site):
    from django.contrib.admin.util import quote
    from django.utils.html import escape
    from django.utils.text import capfirst
    def format_callback(obj, date=None):
        has_admin = obj.__class__ in admin_site._registry
        opts = obj._meta

        if has_admin:
            admin_url = reverse('%s:%s_%s_change'
                                % (admin_site.name,
                                   opts.app_label,
                                   opts.object_name.lower()),
                                None, (quote(obj._get_pk_val()),))
            p = '%s.%s' % (opts.app_label,
                           opts.get_delete_permission())
            if not user.has_perm(p):
                perms_needed.add(opts.verbose_name)
            # Display a link to the admin page.
            return mark_safe(u'%s: <a href="%s">%s</a> (%s)' %
                             (escape(capfirst(opts.verbose_name)),
                              admin_url,
                              escape(obj),
                              date))
        else:
            # Don't display link to edit, because it either has no
            # admin or is edited inline.
            return u'%s: %s' % (capfirst(opts.verbose_name),
                                force_unicode(obj))

    return format_callback
    
    
def get_format_callback2(opts, user, admin_site):
    from django.contrib.admin.util import quote
    from django.utils.html import escape
    from django.utils.text import capfirst
    def format_callback(obj, periods):
        has_admin = obj.__class__ in admin_site._registry
        opts = obj._meta

        out = "" 
        for period in periods:
            out += " (%s-%s) -" % (period.start_date, period.end_date)
        out = out[:-2]

        if has_admin:
            admin_url = reverse('%s:%s_%s_change'
                                % (admin_site.name,
                                   opts.app_label,
                                   opts.object_name.lower()),
                                None, (quote(obj._get_pk_val()),))
            p = '%s.%s' % (opts.app_label,
                           opts.get_delete_permission())
            if not user.has_perm(p):
                perms_needed.add(opts.verbose_name)
            # Display a link to the admin page.

            return mark_safe(u'%s: <a href="%s">%s</a>%s' %
                             (escape(capfirst(opts.verbose_name)),
                              admin_url,
                              escape(obj), out))
        else:
            # Don't display link to edit, because it either has no
            # admin or is edited inline.
            return u'%s: %s%s' % (capfirst(opts.verbose_name),
                                force_unicode(obj), out)

    return format_callback
 
 
 
def rec_contract_collector(contracts, flat, format):
    result= []
    for contract in contracts:
        if contract not in flat:
            content_object = contract.content_object
            if content_object:
                related_contracts = []
                # FK
                for related in content_object._meta.get_all_related_objects():
                    model = related.model
                    instances = model.objects.filter(**{'%s' % (related.field.name): content_object})
                    if Service in model.__bases__:
                        for instance in instances:
                            related_contracts.append(instance.contract)
                    elif model == Contract:
                        ct = ContentType.objects.get_for_model(Contact)
                        for instance in instances.exclude(content_type=ct):
                            related_contracts.append(instance)
                flat.update([contract])
                result.append(format(contract))
                contract_deps = rec_contract_collector(related_contracts, flat, format)
                                    
                # M2M
                for related in content_object._meta.get_all_related_many_to_many_objects():
                    model = related.model
                    field = related.field
                    #TODO has m2m_delete property
                    if not field.null:
                        instances = getattr(content_object, '%s_set' % (model.__name__.lower())).all()
                        _result = []
                        #TODO if instance or childs are not base service skip
                        for instance in instances:
                            _contracts = set()
                            for rel_obj in getattr(instance, field.name).all(): 
                                if hasattr(rel_obj, 'get_base_service_child'):
                                    rel_obj = rel_obj.get_base_service_child()
                                _contracts.update([rel_obj.contract])
                            if _contracts.intersection(flat) == _contracts:
                                contract = instance.contract
                                if contract not in flat:
                                    flat.update([contract])
                                    contract_deps.append(format(contract))
                                    _contract_deps = rec_contract_collector(related_contracts, flat, format)
                                    if _contract_deps:
                                        contract_deps.append(_contract_deps)
                if contract_deps: 
                    result.append(contract_deps)
    return result   
    

def collect_contracts(contracts, user, modeladmin):

    admin_site = modeladmin.admin_site
    opts = modeladmin.model._meta
    format = get_format_callback(opts, user, admin_site)
    flat_contracts = set()
    contract_structre = rec_contract_collector(contracts, flat_contracts, format)
    flat_contracts = list(flat_contracts)
    
    return contract_structre, flat_contracts

def rec_delete_collector(deletable_objects, format):
    leng = len(deletable_objects)
    ix = 0
    structure = []
    while ix < leng:
        obj = deletable_objects[ix]
        cls = obj.__class__
        if cls == list: 
            structure.append(rec_delete_collector(obj, format))
        else:
            if Service in cls.__bases__:
                contract = obj.contract
                if not contract.content_object_is_deletable:
                    if ix+1 < leng and isinstance(deletable_objects[ix+1], list):
                        deletable_objects.pop(ix+1)
                        leng -=1
                    deletable_objects.pop(ix)
                    leng -=1
                    ix -= 1
                else: structure.append(format(obj))
            else: structure.append(format(obj))
        ix +=1
    return structure    


def collect_deletable_objects(contracts, user, modeladmin):
    admin_site = modeladmin.admin_site
    opts = modeladmin.model._meta
    using = router.db_for_write(modeladmin.model)
    
    content_objects=[]
    for contract in contracts:
        content_object = contract.content_object
        content_objects.append(content_object)
    
    collector = NestedObjects(using=using)
    deletable_objects_structure = []
    g_content_objects = group_by(list, '__class__', content_objects, dictionary=True, queryset=False)
    
    flat_objects = []
    for cls in g_content_objects.keys():
        current_objects = g_content_objects[cls]
        collector.collect(current_objects)    
        if Contract.content_objects_are_deletable(cls):
            flat_objects.extend(current_objects)
    
    format = get_format_callback(opts, user, admin_site)
    objects_structure = rec_delete_collector(collector.nested(), format)

    flat_objects = []
    for o_list in g_content_objects.values():
        flat_objects.extend(o_list)
    
    return objects_structure, flat_objects
    



def cancel_contract_view(modeladmin, request, contracts, contacts=[]):
    """
    This view first displays a confirmation page whichs shows all the
    deleteable objects, or, if the user has no permission one of the related
    childs (foreignkeys), a "permission denied" message.

    Next, it cancels all selected objects, deletes their related objects, 
    and redirects back to the change list.
    """
    from common.utils.models import group_by
    
    opts = modeladmin.model._meta
    app_label = opts.app_label

    # Check that the user has delete permission for the actual model
    if not modeladmin.has_delete_permission(request):
        raise PermissionDenied

    user = request.user

    contracts_structure, flat_contracts = collect_contracts(contracts, user, modeladmin)
    objects_structure, flat_objects = collect_deletable_objects(flat_contracts, user, modeladmin)

    
    
    protected = False
    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.
    if request.POST.get('post'):
        n = contracts.count()
        if n:
            for contract in flat_contracts:
                contract.cancel()
            for obj in flat_objects:
                obj_display = force_unicode(obj)
                obj.delete()        
                modeladmin.log_deletion(request, obj, obj_display)
            modeladmin.message_user(request, _("Successfully canceled %(count)d %(items)s.") % {
                "count": contracts.count(), "items": admin.util.model_ngettext(modeladmin.opts, n)
            })
            # Return None to display the change list page again.
            return None

    if len(contracts) == 1:
        objects_name = force_unicode(opts.verbose_name)
    else:
        objects_name = force_unicode(opts.verbose_name_plural)

    title = _("Are you fucking sure?")
    
    #TODO: if contract is alredy canceled, show warn and do nothing.
    context = {
        "title": title,
        "objects_name": objects_name,
        "deletable_objects": [objects_structure],
        "cancelable_contracts": [contracts_structure],
        'queryset': contracts,
        "perms_lacking": False,
        "protected": protected,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return render_to_response("admin/contacts/contract/cancel_contract_confirmation.html", context, context_instance=template.RequestContext(request))
    

def cancel_contract(modeladmin, request, queryset):
    return cancel_contract_view(modeladmin, request, queryset)


def unsubscribe(modeladmin, request, queryset):
    contacts_pk = queryset.values_list('pk', flat=True)
    ct = ContentType.objects.get_for_model(Contact)
    contracts = Contract.objects.active().filter(contact__pk__in=contacts_pk).exclude(content_type=ct, object_id__in=contacts_pk)
    return cancel_contract_view(modeladmin, request, contracts, contacts=queryset)

def bill_contacts(modeladmin, request, queryset):
    pass

def bill_contracts(modeladmin, request, queryset):
    pass 


from django import forms
from common.forms import FormAdminDjango
from datetime import datetime
from django.contrib.admin.widgets import AdminSplitDateTime
class ScheduleCancelForm(forms.Form, FormAdminDjango):
    date = forms.DateTimeField(widget=AdminSplitDateTime(), initial=datetime.now())

class ConfirmCancelForm(forms.Form):
    date = forms.DateTimeField(widget=forms.HiddenInput())


class ScheduleDeactivationForm(forms.Form, FormAdminDjango):
    start_date = forms.DateTimeField(widget=AdminSplitDateTime(), initial=datetime.now())
    end_date = forms.DateTimeField(widget=AdminSplitDateTime(), required=False)

class ConfirmDeactivationForm(forms.Form):
    start_date = forms.DateTimeField(widget=forms.HiddenInput())
    end_date = forms.DateTimeField(widget=forms.HiddenInput())

#from contacts.helpers import _get_all_related_objects, dep_tree, rec_date, node_dep_tree
#from contacts.helpers2 import rec_cancel_date_tree, date_node, create_cancel_dates
#from contacts.helpers8 import pre_schedule_cancel, cancel_date_list, parent_dict,create_cancel_dates, pre_schedule_deactivation, deactivation_date_list
def confirm_scheduled_cancel_view(modeladmin, request, queryset, date=datetime.now()): pass
#    #TODO: perque es repeteix?
#    opts = modeladmin.model._meta
#    app_label = opts.app_label

#    related_objects = []
#    flat = []

#    dictionary = parent_dict()
#    nodes = pre_schedule_cancel(queryset, date, dictionary)    
#    deps = []
#    dates = []
#    _contracts = []
#    user = request.user
#    format = get_format_callback(opts, user, modeladmin.admin_site)
#    #from helpers2 import cancel_date_list
#    for n in nodes:
#        cdl = cancel_date_list(n, format)
#        _contracts.append(cdl[1])
#        dates.append(cdl[0])
#            
#    if request.POST.get('post') == 'confirm_schedule':  
#        form = ConfirmCancelForm(request.POST)
#        if form.is_valid():
#            #date = form.cleaned_data['date']
#            for n in nodes:
#                create_cancel_dates(n)
#        return None
#    form = ConfirmCancelForm(initial={ 'date': date })
#    context = {
#        "title": 'Confirm Schedule Cancelation',
#        "form": form,
#        "opts": opts,
#        "related_contracts_message": 'The following contracts will be Canceled:',
#        "related_contracts": _contracts,
#        "related_objects_message": 'The following objects will be deleted:',
#        "related_objects": dates,
#        "app_label": app_label,
#        "queryset": queryset,
#        'action_name': 'schedule_cancelation',
#        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
#    }
#    return render_to_response("admin/contacts/contract/confirm_schedule.html", context, 
#                              context_instance=template.RequestContext(request))
#                              
                              
def schedule_cancelation(modeladmin, request, queryset): pass
#    opts = modeladmin.model._meta
#    app_label = opts.app_label
#    
#    if request.POST.get('post') == 'schedule_form':
#        form = ScheduleCancelForm(request.POST)
#        if form.is_valid():
#            date = form.cleaned_data['date']
#            return confirm_scheduled_cancel_view(modeladmin, request, queryset, date)
#            
#    elif request.POST.get('post') == 'confirm_schedule':
#        form = ConfirmCancelForm(request.POST)
#        if form.is_valid():
#            date = form.cleaned_data['date']
#            return confirm_scheduled_cancel_view(modeladmin, request, queryset, date)

#    form = ScheduleCancelForm()

#    context = {
#        "title": 'Schedule Cancelation',
#        "form": form,
#        "opts": opts,
#        "app_label": app_label,
#        "queryset": queryset,
#        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
#        'action_name': 'schedule_cancelation',
#    }
#    return render_to_response("admin/contacts/contract/schedule.html", context, 
#                              context_instance=template.RequestContext(request))






def confirm_scheduled_deactivation_view(modeladmin, request, queryset, start_date=datetime.now(), end_date=None):
    opts = modeladmin.model._meta
    app_label = opts.app_label

    related_objects = []
    flat = []

    dictionary = parent_dict()
    nodes = pre_schedule_deactivation(queryset, start_date, end_date,dictionary)
    deps = []
    dates = []
    _contracts = []
    user = request.user
    format = get_format_callback2(opts, user, modeladmin.admin_site)

    for n in nodes:
        cdl = deactivation_date_list(n, format)
        print cdl
        print 'cd'
        _contracts.append(cdl[1])
        dates.append(cdl[0])
    if request.POST.get('post') == 'confirm_schedule':  
        form = ConfirmDeactivationForm(request.POST)
        if form.is_valid():
            #start_date = form.cleaned_data['start_date']
            #end_date = form.cleaned_data['end_date']
            for n in nodes:
                create_cancel_dates(n)
        return None
        
    form = ConfirmDeactivationForm(initial={ 'start_date': start_date, 'end_date': end_date })
    print 'aaaaaaaaaaaaa'
    print _contracts
    context = {
        "title": 'Confirm Scheduled Deactivation',
        "form": form,
        "opts": opts,
        "related_contracts_message": 'The following contracts will be disabled:',
        "related_contracts": _contracts,
        "related_objects_message": 'The following objects will be disabled:',
        "related_objects": dates,
        "app_label": app_label,
        "queryset": queryset,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        'action_name': 'schedule_deactivation',        
    }
    return render_to_response("admin/contacts/contract/confirm_schedule.html", context, 
                              context_instance=template.RequestContext(request))
                              

def schedule_deactivation(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    if request.POST.get('post') == 'schedule_form':
        form = ScheduleDeactivationForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            return confirm_scheduled_deactivation_view(modeladmin, request, queryset, start_date, end_date)
            
    elif request.POST.get('post') == 'confirm_schedule':
        form = ConfirmDeactivationForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            return confirm_scheduled_deactivation_view(modeladmin, request, queryset, start_date, end_date)

    form = ScheduleDeactivationForm()

    context = {
        "title": 'Schedule Deactivation',
        "form": form,
        "opts": opts,
        "app_label": app_label,
        "queryset": queryset,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        'action_name': 'schedule_deactivation',
    }
    return render_to_response("admin/contacts/contract/schedule.html", context, 
                              context_instance=template.RequestContext(request))


def disable_contract(modeladmin, request, contracts):
    opts = modeladmin.model._meta
    app_label = opts.app_label

    # Check that the user has delete permission for the actual model
    if not modeladmin.has_delete_permission(request):
        raise PermissionDenied

    user = request.user
    contract_structure, flat_contracts = collect_contracts(contracts, user, modeladmin)
    
    title = _("Are you fucking sure?")
    protected = False
    #TODO: if contract is alredy disabled, show warn and do nothing.
    context = {
        "title": title,
        "objects_name": 'contracts',
        "cancelable_contracts": [contract_structure],
        'queryset': contracts,
        "perms_lacking": False,
        "protected": protected,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        'action_name': 'disable_contract',
    }
    
    # Display the confirmation page
    return render_to_response("admin/contacts/contract/cancel_contract_confirmation.html", context, context_instance=template.RequestContext(request))
       
       
 
