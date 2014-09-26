from django.db import transaction
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _


@transaction.atomic
def update_orders(modeladmin, request, queryset):
    for service in queryset:
        service.update_orders()
        modeladmin.log_change(request, service, 'Update orders')
    msg = _("Orders for %s selected services have been updated.") % queryset.count()
    modeladmin.message_user(request, msg)
update_orders.url_name = 'update-orders'
update_orders.verbose_name = _("Update orders")


def view_help(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    context = {
        'title': _("Need some help?"),
        'opts': opts,
        'queryset': queryset,
        'obj': queryset.get(),
        'action_name': _("help"),
        'app_label': opts.app_label,
    }
    return TemplateResponse(request, 'admin/services/service/help.html', context)
view_help.url_name = 'help'
view_help.verbose_name = _("Help")
