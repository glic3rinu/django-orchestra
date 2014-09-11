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

