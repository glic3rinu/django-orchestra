from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class ActiveOrderListFilter(SimpleListFilter):
    """ Filter tickets by created_by according to request.user """
    title = _("is active")
    parameter_name = 'is_active'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("Active")),
            ('False', _("Inactive")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.active()
        elif self.value() == 'False':
            return queryset.inactive()
        return queryset


class BilledOrderListFilter(SimpleListFilter):
    """ Filter tickets by created_by according to request.user """
    title = _("billed")
    parameter_name = 'pending'
    
    def lookups(self, request, model_admin):
        return (
            ('to_date', _("To date")),
            ('full', _("Full period")),
            ('not', _("Not billed")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'to_date':
            return queryset.filter(billed_until__isnull=False,
                    billed_until__gte=timezone.now())
        elif self.value() == 'full':
            raise NotImplementedError
        elif self.value() == 'not':
            return queryset.filter(
                Q(billed_until__isnull=True) |
                Q(billed_until__lt=timezone.now())
            )
        return queryset
