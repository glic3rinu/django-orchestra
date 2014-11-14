from functools import partial

from django import forms
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.admin.decorators import action_with_confirmation
from orchestra.admin.utils import change_url
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
