from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext as _


class UsedContentTypeFilter(SimpleListFilter):
    title = _('Content type')
    parameter_name = 'content_type'
    
    def lookups(self, request, model_admin):
        qset = model_admin.model._default_manager.all().order_by()
        result = ()
        for pk, name in qset.values_list('content_type', 'content_type__model').distinct():
            result += ((str(pk), name.capitalize()),)
        return result
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type=self.value())
