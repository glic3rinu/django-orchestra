from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class ActiveOrderListFilter(SimpleListFilter):
    """ Filter tickets by created_by according to request.user """
    title = 'Orders'
    parameter_name = 'is_active'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("Active")),
            ('False', _("Inactive")),
            ('None', _("All")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.active()
        elif self.value() == 'False':
            return queryset.inactive()
        return queryset

    def choices(self, cl):
        """ Remove default All """
        choices = iter(super(ActiveOrderListFilter, self).choices(cl))
        choices.next()
        return choices
