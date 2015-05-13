from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class IsMainListFilter(SimpleListFilter):
    """ Filter Nodes by group according to request.user """
    title = _("main")
    parameter_name = 'is_main'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("Yes")),
            ('False', _("No")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.by_is_main()
        if self.value() == 'False':
            return queryset.by_is_main(is_main=False)
