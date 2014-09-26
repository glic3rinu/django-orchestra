from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _


def view_zone(modeladmin, request, queryset):
    zone = queryset.get()
    context = {
        'opts': modeladmin.model._meta,
        'object': zone,
        'title': _("%s zone content") % zone.origin.name
    }
    return TemplateResponse(request, 'admin/domains/domain/view_zone.html', context)
view_zone.url_name = 'view-zone'
view_zone.verbose_name = _("View zone")
