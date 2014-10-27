from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.utils.translation import ungettext, ugettext_lazy as _


@transaction.atomic
def run_monitor(modeladmin, request, queryset):
    for resource in queryset:
        resource.monitor()
        modeladmin.log_change(request, resource, _("Run monitors"))
    num = len(queryset)
    msg = ungettext(
        _("One selected resource has been monitored."),
        _("%s selected resource have been monitored.") % num,
        num)
    modeladmin.message_user(request, msg)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
run_monitor.url_name = 'monitor'
