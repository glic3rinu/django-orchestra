import os

from django import forms
from django.contrib import messages, admin
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.admin.decorators import action_with_confirmation
from orchestra.contrib.orchestration.middlewares import OperationsMiddleware

from .forms import GrantPermissionForm


def grant_permission(modeladmin, request, queryset):
    account_id = None
    for user in queryset:
        account_id = account_id or user.account_id
        if user.account_id != account_id:
            messages.error("Users from the same account should be selected.")
    user = queryset[0]
    if request.method == 'POST':
        form = GrantPermissionForm(user, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            to = os.path.join(cleaned_data['base_path'], cleaned_data['path_extension'])
            ro = cleaned_data['read_only']
            for user in queryset:
                user.grant_to = to
                user.grant_ro = ro
                OperationsMiddleware.collect('grant_permission', instance=user)
                context = {
                    'type': _("read-only") if ro else _("read-write"),
                    'to': to,
                }
                msg = _("Granted %(type)s permissions on %(to)s") % context
                modeladmin.log_change(request, user, msg)
            return
    opts = modeladmin.model._meta
    app_label = opts.app_label
    context = {
        'title': _("Grant permission"),
        'action_name': _("Grant permission"),
        'action_value': 'grant_permission',
        'queryset': queryset,
        'opts': opts,
        'obj': user,
        'app_label': app_label,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        'form': GrantPermissionForm(user),
    }
    return TemplateResponse(request, 'admin/systemusers/systemuser/grant_permission.html',
        context, current_app=modeladmin.admin_site.name)
grant_permission.url_name = 'grant-permission'
grant_permission.verbose_name = _("Grant permission")


def delete_selected(modeladmin, request, queryset):
    """ wrapper arround admin.actions.delete_selected to prevent main system users deletion """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    # Check that the user has delete permission for the actual model
    if not modeladmin.has_delete_permission(request):
        raise PermissionDenied
    else:
        accounts = []
        for user in queryset:
            if user.is_main:
                accounts.append(user.username)
        if accounts:
            n = len(accounts)
            messages.error(request, ungettext(
                "You have selected one main system user (%(accounts)s), which can not be deleted.",
                "You have selected some main system users which can not be deleted (%(accounts)s).",
                n) % {
                    'accounts': ', '.join(accounts[:10]+['...'] if n > 10 else accounts)
                }
            )
            return
    return admin.actions.delete_selected(modeladmin, request, queryset)
delete_selected.short_description = _("Delete selected %(verbose_name_plural)s")

