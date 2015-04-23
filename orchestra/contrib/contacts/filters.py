from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from .models import Contact


class EmailUsageListFilter(SimpleListFilter):
    title = _("email usages")
    parameter_name = 'email_usages'
    
    def lookups(self, request, model_admin):
        return Contact.EMAIL_USAGES
    
    def queryset(self, request, queryset):
        value = self.value()
        if value is None:
            return queryset
        return queryset.filter(email_usages=value.split(','))
