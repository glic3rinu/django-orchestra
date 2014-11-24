from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class TopDomainListFilter(SimpleListFilter):
    """ Filter Nodes by group according to request.user """
    title = _("top domains")
    parameter_name = 'top_domain'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("Top domains")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(top__isnull=True)
