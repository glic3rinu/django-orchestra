from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext, ugettext_lazy as _


def run_monitor(modeladmin, request, queryset):
    """ Resource and ResourceData run monitors """
    referer = request.META.get('HTTP_REFERER')
    async = modeladmin.model.monitor.__defaults__[0]
    logs = set()
    for resource in queryset:
        rlogs = resource.monitor()
        if not async:
            logs = logs.union(set([str(log.pk) for log in rlogs]))
        modeladmin.log_change(request, resource, _("Run monitors"))
    if async:
        num = len(queryset)
        # TODO listfilter by uuid: task.request.id + ?task_id__in=ids
        link = reverse('admin:djcelery_taskstate_changelist')
        msg = ungettext(
            _("One selected resource has been <a href='%s'>scheduled for monitoring</a>.") % link,
            _("%s selected resource have been <a href='%s'>scheduled for monitoring</a>.") % (num, link),
            num)
    else:
        num = len(logs)
        if num == 1:
            log_pk = int(logs.pop())
            link = reverse('admin:orchestration_backendlog_change', args=(log_pk,))
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


def show_history(modeladmin, request, queryset):
    context = {
        'ids': ','.join(map(str, queryset.values_list('id', flat=True))),
    }
    return render(request, 'admin/resources/resourcedata/history.html', context)
