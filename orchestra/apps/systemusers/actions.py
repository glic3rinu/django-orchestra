from django import forms
from django.contrib import messages, admin
from django.core.exceptions import PermissionDenied
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.admin.decorators import action_with_confirmation
from orchestra.apps.orchestration.models import BackendOperation as Operation


class GrantPermissionForm(forms.Form):
    base_path = forms.ChoiceField(label=_("Grant access to"), choices=(('hola', 'hola'),),
        help_text=_("User will be granted access to this directory."))
    path_extension = forms.CharField(label='', required=False)
    read_only = forms.BooleanField(label=_("Read only"), initial=False, required=False,
            help_text=_("Designates whether the permissions granted will be read-only or read/write."))


@action_with_confirmation(extra_context=dict(form=GrantPermissionForm()))
def grant_permission(modeladmin, request, queryset):
    user = queryset.get()
    log = Operation.execute_action(user, 'grant_permission')
    # TODO
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

