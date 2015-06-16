from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class ResourceDataListFilter(SimpleListFilter):
    """ Mock filter to avoid e=1 """
    title = _("Resource data")
    parameter_name = 'resource_data'
    
    def lookups(self, request, model_admin):
        return ()
    
    def queryset(self, request, queryset):
        return queryset
    
    def choices(self, cl):
        return []
