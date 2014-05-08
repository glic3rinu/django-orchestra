from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class HasInvoiceContactListFilter(SimpleListFilter):
    """ Filter Nodes by group according to request.user """
    title = _("has invoice contact")
    parameter_name = 'invoice'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("Yes")),
            ('False', _("No")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(invoicecontact__isnull=False)
        if self.value() == 'False':
            return queryset.filter(invoicecontact__isnull=True)
