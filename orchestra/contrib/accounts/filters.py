from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


class IsActiveListFilter(SimpleListFilter):
    title = _("is active")
    parameter_name = 'active'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("Yes")),
            ('False', _("No")),
            ('account', _("Account disabled")),
            ('object', _("Object disabled")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(is_active=True, account__is_active=True)
        elif self.value() == 'False':
            return queryset.filter(Q(is_active=False) | Q(account__is_active=False))
        elif self.value() == 'account':
            return queryset.filter(account__is_active=False)
        elif self.value() == 'object':
            return queryset.filter(is_active=False)
        return queryset
