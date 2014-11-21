from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext, ugettext_lazy as _


def run_monitor(modeladmin, request, queryset):
    """ Resource and ResourceData run monitors """
    referer = request.META.get('HTTP_REFERER')
    if not queryset:
        modeladmin.message_user(request, _("No resource has been selected,"))
        return redirect(referer)
    async = modeladmin.model.monitor.func_defaults[0]
    results = []
    for resource in queryset:
        result = resource.monitor()
        if not async:
            results += result
        modeladmin.log_change(request, resource, _("Run monitors"))
    num = len(queryset)
    if async:
        link = reverse('admin:djcelery_taskstate_changelist')
        msg = ungettext(
            _("One selected resource has been <a href='%s'>scheduled for monitoring</a>.") % link,
            _("%s selected resource have been <a href='%s'>scheduled for monitoring</a>.") % (num, link),
            num)
    else:
        if len(results) == 1:
            log = results[0].log
            link = reverse('admin:orchestration_backendlog_change', args=(log.pk,))
            msg = _("One selected resource has <a href='%s'>been monitored</a>.") % link
        elif len(results) >= 1:
            logs = [str(result.log.pk) for result in results]
            link = reverse('admin:orchestration_backendlog_changelist')
            link += '?id__in=%s' % ','.join(logs)
            msg = _("%s selected resources have <a href='%s'>been monitored</a>.") % (num, link)
        else:
            msg = _("No related monitors have been executed.")
    modeladmin.message_user(request, mark_safe(msg))
    if referer:
        return redirect(referer)
run_monitor.url_name = 'monitor'
