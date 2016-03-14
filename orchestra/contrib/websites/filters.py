from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class HasWebAppsListFilter(SimpleListFilter):
    """ Filter addresses whether they have any webapp or not """
    title = _("has webapps")
    parameter_name = 'has_webapps'
    
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


class HasDomainsFilter(HasWebAppsListFilter):
    """ Filter addresses whether they have any domains or not """
    title = _("has domains")
    parameter_name = 'has_domains'
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(domains__isnull=False)
        elif self.value() == 'False':
            return queryset.filter(domains__isnull=True)
        return queryset
