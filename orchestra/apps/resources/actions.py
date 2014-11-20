from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.utils.translation import ungettext, ugettext_lazy as _


def run_monitor(modeladmin, request, queryset):
    """ Resource and ResourceData run monitors """
    referer = request.META.get('HTTP_REFERER')
    if not queryset:
        modeladmin.message_user(request, _("No resource has been selected,"))
        return redirect(referer)
    for resource in queryset:
        resource.monitor()
        modeladmin.log_change(request, resource, _("Run monitors"))
    num = len(queryset)
    async = resource.monitor.func_defaults[0]
    if async:
        # TODO schedulet link to celery taskstate page
        msg = ungettext(
            _("One selected resource has been scheduled for monitoring."),
            _("%s selected resource have been scheduled for monitoring.") % num,
            num)
    else:
        msg = ungettext(
            _("One selected resource has been monitored."),
            _("%s selected resource have been monitored.") % num,
            num)
    modeladmin.message_user(request, msg)
    if referer:
        return redirect(referer)
run_monitor.url_name = 'monitor'
