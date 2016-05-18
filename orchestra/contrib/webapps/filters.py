from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from .types import AppType


class HasWebsiteListFilter(SimpleListFilter):
    title = _("website")
    parameter_name = 'has_website'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("True")),
            ('False', _("False")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(content__isnull=False)
        elif self.value() == 'False':
            return queryset.filter(content__isnull=True)
        return queryset


class DetailListFilter(SimpleListFilter):
    title = _("detail")
    parameter_name = 'detail'
    
    def lookups(self, request, model_admin):
        ret = set([('empty', _("Empty"))])
        lookup_map = {}
        for apptype in AppType.get_plugins():
            for field, values in apptype.get_detail_lookups().items():
                for value in values:
                    lookup_map[value[0]] = field
                    ret.add(value)
        self.lookup_map = lookup_map
        return sorted(list(ret), key=lambda e: e[1])
    
    def queryset(self, request, queryset):
        value = self.value()
        if value:
            if value == 'empty':
                return queryset.filter(data={})
            try:
                field = self.lookup_map[value]
            except KeyError:
                return queryset
            else:
                return queryset.filter(data__contains='"%s":"%s"' % (field, value))
        return queryset
