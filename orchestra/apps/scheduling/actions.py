from django import template
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.admin.util import get_deleted_objects, model_ngettext
from django.db import router, transaction
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _


@transaction.commit_on_success
def revoke(modeladmin, request, queryset):
    if queryset.filter(snapshot=True): 
        messages.add_message(request, messages.ERROR, "Snapshots can not be revoked")
        return None
    for schedule in queryset:
        schedule.revoke()
    modeladmin.message_user(request, _("All %d selected scheduling are successfully revoked" % queryset.count()))
revoke.short_description = _("Revoke scheduling")


@transaction.commit_on_success
def confirm_schedule(modeladmin, request, queryset, data, HiddenForm, action_name, set_method):
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

    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.
    if request.POST.get('post') == 'confirm_schedule':
        if perms_needed:
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                getattr(obj, set_method)(**data)
            modeladmin.message_user(request, _("Successfully scheduled %(count)d for %(items)s.") % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
        # Return None to display the change list page again.
        return None

    if len(queryset) == 1:
        objects_name = force_unicode(opts.verbose_name)
    else:
        objects_name = force_unicode(opts.verbose_name_plural)

    if perms_needed or protected:
        title = _("Cannot schedule %(name)s") % {"name": objects_name}
    else:
        title = _("Are you sure?")
    
    context = {
        "title": title,
        "objects_name": objects_name,
        "deletable_objects": [deletable_objects],
        'queryset': queryset,
        "perms_lacking": perms_needed,
        "protected": protected,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'action_name': action_name,
        'form': HiddenForm(initial=data),
    }

    # Display the confirmation page
    return render_to_response("admin/scheduling/confirm_schedule.html", context, 
                              context_instance=template.RequestContext(request))    


def schedule(modeladmin, request, queryset, Form, HiddenForm, title, action_name, set_method):
    opts = modeladmin.model._meta
    app_label = opts.app_label
    if request.POST.get('post') == 'schedule_form':
        form = Form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            return confirm_schedule(modeladmin, request, queryset, data, HiddenForm, action_name, set_method)
            
    elif request.POST.get('post') == 'confirm_schedule':
        form = HiddenForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            return confirm_schedule(modeladmin, request, queryset, data, HiddenForm, action_name, set_method)

    form = Form()
    context = {
        "title": title, 
        "form": form,
        "opts": opts,
        "app_label": app_label,
        "queryset": queryset,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        'action_name': action_name,
    }
    return render_to_response("admin/scheduling/schedule.html", context, 
                              context_instance=template.RequestContext(request))



