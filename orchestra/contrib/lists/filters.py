from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class HasCustomAddressListFilter(SimpleListFilter):
    """ Filter addresses whether they have any webapp or not """
    title = _("has custom address")
    parameter_name = 'has_custom_address'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("True")),
            ('False', _("False")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.exclude(address_name='')
        elif self.value() == 'False':
            return queryset.filter(address_name='')
        return queryset
