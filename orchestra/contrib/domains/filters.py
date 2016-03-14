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


class HasWebsiteFilter(SimpleListFilter):
    """ Filter addresses whether they have any websites or not """
    title = _("has websites")
    parameter_name = 'has_websites'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("True")),
            ('False', _("False")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(websites__isnull=False)
        elif self.value() == 'False':
            return queryset.filter(websites__isnull=True)
        return queryset


class HasAddressFilter(HasWebsiteFilter):
    """ Filter addresses whether they have any addresses or not """
    title = _("has addresses")
    parameter_name = 'has_addresses'
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(addresses__isnull=False)
        elif self.value() == 'False':
            return queryset.filter(addresses__isnull=True)
        return queryset
