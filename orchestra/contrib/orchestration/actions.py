from django.contrib import messages
from django.contrib.admin import helpers
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.admin.utils import get_object_from_url, change_url
from orchestra.contrib.orchestration.helpers import message_user

from . import Operation
from .models import BackendOperation


def retry_backend(modeladmin, request, queryset):
    related_operations = queryset.values_list('operations__id', flat=True).distinct()
    related_operations = BackendOperation.objects.filter(pk__in=related_operations)
    related_operations = related_operations.select_related('log__server').prefetch_related('instance')
    if request.POST.get('post') == 'generic_confirmation':
        operations = []
        for operation in related_operations:
            if operation.instance:
                op = Operation.load(operation)
                operations.append(op)
        if not operations:
            messages.warning(request, _("No backend operation has been executed."))
        else:
            logs = Operation.execute(operations)
            message_user(request, logs)
        Operation.execute(operations)
        return
    opts = modeladmin.model._meta
    display_objects = []
    deleted_objects = []
    for op in related_operations:
        if not op.instance:
            deleted_objects.append(op)
        else:
            context = {
                'backend': op.log.backend,
                'action': op.action,
                'instance': op.instance,
                'instance_url': change_url(op.instance),
                'server': op.log.server,
                'server_url': change_url(op.log.server),
            }
            display_objects.append(mark_safe(
                '%(backend)s.%(action)s(<a href="%(instance_url)s">%(instance)s</a>) @ <a href="%(server_url)s">%(server)s</a>' % context
            ))
    context = {
        'title': _("Are you sure to execute the following backends?"),
        'action_name': _('Retry backend'),
        'action_value': 'retry_backend',
        'display_objects': display_objects,
        'deleted_objects': deleted_objects,
        'queryset': queryset,
        'opts': opts,
        'app_label': opts.app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'obj': get_object_from_url(modeladmin, request),
    }
    return render(request, 'admin/orchestration/backends/retry.html', context)
retry_backend.short_description = _("Retry")
retry_backend.url_name = 'retry'
