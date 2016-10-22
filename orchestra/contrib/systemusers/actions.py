import os

from django.contrib import messages, admin
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.contrib.orchestration import Operation, helpers

from .forms import PermissionForm, LinkForm


def get_verbose_choice(choices, value):
    for choice, verbose in choices:
        if choice == value:
            return verbose


def set_permission(modeladmin, request, queryset):
    account_id = None
    for user in queryset:
        account_id = account_id or user.account_id
        if user.account_id != account_id:
            messages.error(request, "Users from the same account should be selected.")
            return
    user = queryset[0]
    form = PermissionForm(user)
    action_value = 'set_permission'
    if request.POST.get('post') == 'generic_confirmation':
        form = PermissionForm(user, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            operations = []
            for user in queryset:
                base_home = cleaned_data['base_home']
                extension = cleaned_data['home_extension']
                action = cleaned_data['set_action']
                perms = cleaned_data['permissions']
                user.set_perm_action = action
                user.set_perm_base_home = base_home
                user.set_perm_home_extension = extension
                user.set_perm_perms = perms
                operations.extend(Operation.create_for_action(user, 'set_permission'))
                verbose_action = get_verbose_choice(form.fields['set_action'].choices,
                    user.set_perm_action)
                verbose_permissions = get_verbose_choice(form.fields['permissions'].choices,
                    user.set_perm_perms)
                context = {
                    'action': verbose_action,
                    'perms': verbose_permissions.lower(),
                    'to': os.path.join(user.set_perm_base_home, user.set_perm_home_extension),
                }
                msg = _("%(action)s %(perms)s permission to %(to)s") % context
                modeladmin.log_change(request, user, msg)
            if not operations:
                messages.error(request, _("No backend operation has been executed."))
            else:
                logs = Operation.execute(operations)
                helpers.message_user(request, logs)
            return
    opts = modeladmin.model._meta
    app_label = opts.app_label
    context = {
        'title': _("Set permission"),
        'action_name': _("Set permission"),
        'action_value': action_value,
        'queryset': queryset,
        'opts': opts,
        'obj': user,
        'app_label': app_label,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        'form': form,
    }
    return TemplateResponse(request, 'admin/systemusers/systemuser/set_permission.html', context)
set_permission.url_name = 'set-permission'
set_permission.tool_description = _("Set permission")


def create_link(modeladmin, request, queryset):
    account_id = None
    for user in queryset:
        account_id = account_id or user.account_id
        if user.account_id != account_id:
            messages.error(request, "Users from the same account should be selected.")
            return
    user = queryset[0]
    form = LinkForm(user, queryset=queryset)
    action_value = 'create_link'
    if request.POST.get('post') == 'generic_confirmation':
        form = LinkForm(user, request.POST, queryset=queryset)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            operations = []
            for user in queryset:
                base_home = cleaned_data['base_home']
                extension = cleaned_data['home_extension']
                target = os.path.join(base_home, extension)
                default_name = os.path.join(user.home, os.path.basename(target))
                link_name = cleaned_data['link_name'] or default_name
                user.create_link_target = target
                user.create_link_name = link_name
                operations.extend(Operation.create_for_action(user, 'create_link'))
                context = {
                    'target': target,
                    'link_name': link_name,
                }
                msg = _("Created link from %(target)s to %(link_name)s") % context
                modeladmin.log_change(request, request.user, msg)
            logs = Operation.execute(operations)
            if logs:
                helpers.message_user(request, logs)
            else:
                messages.error(request, "No backend operation has been executed.")
            return
    opts = modeladmin.model._meta
    app_label = opts.app_label
    context = {
        'title': _("Create link"),
        'action_name': _("Create link"),
        'action_value': action_value,
        'queryset': queryset,
        'opts': opts,
        'obj': user,
        'app_label': app_label,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        'form': form,
    }
    return TemplateResponse(request, 'admin/systemusers/systemuser/create_link.html', context)
create_link.url_name = 'create-link'
create_link.tool_description = _("Create link")


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
