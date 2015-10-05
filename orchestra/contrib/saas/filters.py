from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class CustomURLListFilter(SimpleListFilter):
    title = _("custom URL")
    parameter_name = 'has_custom_url'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("True")),
            ('False', _("False")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.exclude(custom_url='')
        elif self.value() == 'False':
            return queryset.filter(custom_url='')
        return queryset
