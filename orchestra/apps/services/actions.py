from django.contrib.admin import helpers
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import get_object_from_url

@transaction.atomic
def update_orders(modeladmin, request, queryset, extra_context=None):
    if not queryset:
        return
    if request.POST.get('post') == 'confirmation':
        num = 0
        services = []
        for service in queryset:
            updates = service.update_orders()
            num += len(updates)
            services.append(str(service.pk))
            modeladmin.log_change(request, service, _("Orders updated"))
        if num == 1:
            url = reverse('admin:orders_order_change', args=(updates[0][0].pk,))
            msg = _('<a href="%s">One related order</a> has benn updated') % url
        else:
            url = reverse('admin:orders_order_changelist')
            url += '?service__in=%s' % ','.join(services)
            msg = _('<a href="%s">%s related orders</a> have been updated') % (url, num)
        modeladmin.message_user(request, mark_safe(msg))
        return
    updates = []
    for service in queryset:
        updates += service.update_orders(commit=False)
    opts = modeladmin.model._meta
    context = {
        'title': _("Update orders will cause the following."),
        'action_name': 'Update orders',
        'action_value': 'update_orders',
        'updates': updates,
        'queryset': queryset,
        'opts': opts,
        'app_label': opts.app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'obj': get_object_from_url(modeladmin, request),
    }
    return render(request, 'admin/services/service/update_orders.html', context)
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


def clone(modeladmin, request, queryset):
    service = queryset.get()
    fields = (
        'content_type_id', 'match', 'handler_type', 'is_active', 'ignore_superusers', 'billing_period',
        'billing_point', 'is_fee', 'metric', 'nominal_price', 'tax', 'pricing_period', 
        'rate_algorithm', 'on_cancel', 'payment_style',
    )
    query = []
    for field in fields:
        value = getattr(service, field)
        field = field.replace('_id', '')
        query.append('%s=%s' % (field, value))
    opts = service._meta
    url = reverse('admin:%s_%s_add' % (opts.app_label, opts.model_name))
    url += '?%s' % '&'.join(query)
    return redirect(url)
