from collections import OrderedDict

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


def history(modeladmin, request, queryset):
    resources = OrderedDict()
    names = {}
    for data in queryset:
        resource = data.resource
        try:
            objects, totals, all_dates = resources[resource]
        except KeyError:
            objects, totals, all_dates = OrderedDict(), OrderedDict(), set()
            resources[resource] = (objects, totals, all_dates)
        scale = resource.get_scale()
        # Per monitor
        aggregate = len(resource.monitors) > 1
        for monitor, dataset in data.get_monitor_datasets():
            for date, dataset in resource.aggregation_instance.historic_filter(dataset):
                if dataset is None:
                    break
                all_dates.add(date)
                # Per object
                for mdata, usage in resource.aggregation_instance.compute_historic_usage(dataset):
                    # objects
                    usage = float(usage or 0)/scale
                    key = (monitor, mdata.object_id)
                    names[key] = mdata.content_object_repr
                    try:
                        dates = objects[key]
                    except KeyError:
                        dates = {
                            date: usage
                        }
                        objects[key] = dates
                    dates[date] = usage
                    if aggregate:
                        # Totals
                        key = (data)
                        try:
                            dates = totals[data]
                        except KeyError:
                            dates = {
                                date: usage
                            }
                            totals[data] = dates
                        try:
                            dates[date] += usage
                        except KeyError:
                            dates[date] = usage
    results = []
    from .backends import ServiceMonitor
    import json
    from django.template.defaultfilters import date as date_filter
    for resource, content in resources.items():
        object_result = []
        total_result = []
        objects, totals, all_dates = content
        all_dates = list(sorted(all_dates))
        for key, dates in objects.items():
            name = names[key]
            data = []
            for date in all_dates:
                try:
                    data.append(round(dates[date], 2))
                except KeyError:
                    data.append(0)
            object_result.append({
                'name': name,
                'data': data,
            })
        if len(totals) > 1:
            for rdata, dates in totals.items():
                name = rdata.content_object_repr
                data = []
                for date in all_dates:
                    try:
                        data.append(round(dates[date], 2))
                    except KeyError:
                        data.append(0)
                total_result.append({
                    'name': name,
                    'data': data,
                })
        results.append((resource, object_result, total_result, all_dates))
        
        
    context = {
        'resources': results
    }
    return render(request, 'admin/resources/resourcedata/history.html', context)
history.url_name = 'history'
