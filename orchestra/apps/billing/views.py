from models import BillLine
from django import forms
from django.utils.translation import ugettext as _
from itertools import chain

from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from common.widgets import CheckboxSelectMultipleTable

def ListForm_Factory(qset, modeladmin, deps=None, req_post=None, initial=None):

    class ListForm(forms.Form):
        CHOICES = (
            ('I', _('Ignore Order')),
            ('S', _('Reset the Order billed until')),) 
            
        order_effect = forms.ChoiceField(widget=forms.widgets.RadioSelect, choices=CHOICES, initial='S')    
        dependencies = forms.ModelMultipleChoiceField(widget=CheckboxSelectMultipleTable(dep_structure=deps, modeladmin=modeladmin), queryset=qset, required=False)
        
    if req_post: return ListForm(req_post)
    return ListForm       


def delete_lines_view(modeladmin, request, queryset):
    from django.core.exceptions import PermissionDenied
    from django.contrib.admin import helpers
    from django.contrib.admin.util import get_deleted_objects, model_ngettext
    from django.db import router
    from django.template.response import TemplateResponse
    from django.utils.encoding import force_unicode
    
    opts = modeladmin.model._meta
    app_label = opts.app_label

    # Check that the user has delete permission for the actual model
    if not modeladmin.has_delete_permission(request):
        raise PermissionDenied

    using = router.db_for_write(modeladmin.model)

    # Populate deletable_objects, a data structure of all related objects that
    # will also be deleted.
    deletable_objects, perms_needed, protected = get_deleted_objects(
        queryset, opts, request.user, modeladmin.admin_site, using)

    not_in_queryset = {}
    for line in queryset:
        rel_lines = BillLine.objects.get_all_related_pending_lines(line=line, initial_date__gt=line.initial_date, auto=True)
        for rel in rel_lines:
            if not rel in queryset:
                if rel in not_in_queryset: 
                    not_in_queryset[rel].append(line)
                else:
                    not_in_queryset[rel] = [line]
                
    qset = BillLine.objects.filter(id__in=[o.id for o in not_in_queryset])

    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.
    if request.POST.get('post'):
        if perms_needed:
            raise PermissionDenied
        form = ListForm_Factory(qset, modeladmin, req_post=request.POST)
        if form.is_valid():
            chosen_qset = form.cleaned_data['dependencies']
            order_effect = form.cleaned_data['order_effect']
            if chosen_qset: 
                all_qset = set(queryset).union(set(chosen_qset))
                all_qset = BillLine.objects.filter(pk__in=[o.pk for o in all_qset])
            else: all_qset = queryset
            n = all_qset.count() 
            if n:
                if order_effect == 'S':
                    from common.utils.models import group_by
                    from django.db.models import Q
                    from ordering_backend import get_order
                    order_groups = group_by(BillLine, 'order_id', all_qset.filter(auto=True), dictionary=True)
                    print order_groups
                    for order_group in order_groups: 
                        # IF not manual line
                        l_billed_until = order_groups[order_group].order_by('order_billed_until')[0]
                        rel = BillLine.objects.filter(Q(order_id=order_group, 
                            order_billed_until=l_billed_until.order_billed_until, auto=True) & 
                            ~Q(pk__in=all_qset.values_list('pk', flat=True)))
                        # If not remainig lines genered at the same bill momemnt
                        # Reset order values
                        order = get_order(pk=order_group)
                        print rel
                        if not rel:
                            order.billed_until = l_billed_until.order_billed_until
                            order.last_bill_date = l_billed_until.order_last_bill_date
                            order.save()
                        else:
                            l_initial_date = order_groups[order_group].order_by('initial_date')[0] 
                            print l_initial_date
                            print order_groups[order_group].order_by('initial_date').values_list('initial_date')
                            order.billed_until = l_initial_date.initial_date
                            order.save()
                for obj in all_qset:
                    obj_display = force_unicode(obj)
                    modeladmin.log_deletion(request, obj, obj_display)
                    obj.delete()
                modeladmin.message_user(request, _("Successfully deleted %(count)d %(items)s.") % {
                    "count": n, "items": model_ngettext(modeladmin.opts, n) })
            # Return None to display the change list page again.
            return None

    dep_form = ListForm_Factory(qset, modeladmin, deps=not_in_queryset)
    
    if len(queryset) == 1:
        objects_name = force_unicode(opts.verbose_name)
    else:
        objects_name = force_unicode(opts.verbose_name_plural)

    if perms_needed or protected:
        title = _("Cannot delete %(name)s") % {"name": objects_name}
    else:
        title = _("Are you sure?")

    context = {
        "title": title,
        "objects_name": objects_name,
        "deletable_objects": [deletable_objects],
        'queryset': queryset,
        "perms_lacking": perms_needed,
        "form": dep_form,
        "protected": protected,
        "opts": opts,
      #  "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }

    # Display the confirmation page
    return TemplateResponse(request, "admin/billing/billline/delete_selected_confirmation.html", 
        context, current_app=modeladmin.admin_site.name)

