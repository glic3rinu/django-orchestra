from django.contrib import messages
from django.db import transaction
from django.utils.translation import ugettext_lazy as _


@transaction.atomic
def update_orders(modeladmin, request, queryset):
    for service in queryset:
        service.update_orders()
        modeladmin.log_change(request, transaction, 'Update orders')
    msg = _("Orders for %s selected services have been updated.") % queryset.count()
    modeladmin.message_user(request, msg)
update_orders.url_name = 'update-orders'
update_orders.verbose_name = _("Update orders")
