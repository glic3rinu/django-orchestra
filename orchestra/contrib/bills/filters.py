from django.contrib.admin import SimpleListFilter
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class BillTypeListFilter(SimpleListFilter):
    """ Filter tickets by created_by according to request.user """
    title = 'Type'
    parameter_name = ''
    
    def __init__(self, request, *args, **kwargs):
        super(BillTypeListFilter, self).__init__(request, *args, **kwargs)
        self.request = request
    
    def lookups(self, request, model_admin):
        return (
            ('bill', _("All")),
            ('invoice', _("Invoice")),
            ('amendmentinvoice', _("Amendment invoice")),
            ('fee', _("Fee")),
            ('fee', _("Amendment fee")),
            ('proforma', _("Pro-forma")),
        )
    
    def queryset(self, request, queryset):
        return queryset
    
    def value(self):
        return self.request.path.split('/')[-2]
    
    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': reverse('admin:bills_%s_changelist' % lookup),
                'display': title,
            }


class PositivePriceListFilter(SimpleListFilter):
    title = _("positive price")
    parameter_name = 'positive_price'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("Yes")),
            ('False', _("No")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(computed_total__gt=0)
        if self.value() == 'False':
            return queryset.filter(computed_total__lte=0)


class HasBillContactListFilter(SimpleListFilter):
    """ Filter Nodes by group according to request.user """
    title = _("has bill contact")
    parameter_name = 'bill'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("Yes")),
            ('False', _("No")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(billcontact__isnull=False)
        if self.value() == 'False':
            return queryset.filter(billcontact__isnull=True)
