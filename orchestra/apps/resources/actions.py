from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext, ugettext_lazy as _


def run_monitor(modeladmin, request, queryset):
    """ Resource and ResourceData run monitors """
    referer = request.META.get('HTTP_REFERER')
    async = modeladmin.model.monitor.func_defaults[0]
    logs = set()
    for resource in queryset:
        results = resource.monitor()
        if not async:
            for result in results:
                if hasattr(result, 'log'):
                    logs.add(result.log.pk)
        modeladmin.log_change(request, resource, _("Run monitors"))
    if async:
        num = len(queryset)
        link = reverse('admin:djcelery_taskstate_changelist')
        msg = ungettext(
            _("One selected resource has been <a href='%s'>scheduled for monitoring</a>.") % link,
            _("%s selected resource have been <a href='%s'>scheduled for monitoring</a>.") % (num, link),
            num)
    else:
        num = len(logs)
        if num == 1:
            log = logs.pop()
            link = reverse('admin:orchestration_backendlog_change', args=(log,))
            msg = _("One related monitor has <a href='%s'>been executed</a>.") % link
        elif num >= 1:
            link = reverse('admin:orchestration_backendlog_changelist')
            link += '?id__in=%s' % ','.join(logs)
            msg = _("%s related monitors have <a href='%s'>been executed</a>.") % (num, link)
        else:
            msg = _("No related monitors have been executed.")
    modeladmin.message_user(request, mark_safe(msg))
    if referer:
        return redirect(referer)
run_monitor.url_name = 'monitor'
