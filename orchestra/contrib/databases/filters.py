from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class HasUserListFilter(SimpleListFilter):
    """ Filter addresses whether they have any db user or not """
    title = _("has user")
    parameter_name = 'has_user'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("True")),
            ('False', _("False")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(users__isnull=False)
        elif self.value() == 'False':
            return queryset.filter(users__isnull=True)
        return queryset


class HasDatabaseListFilter(HasUserListFilter):
    """ Filter addresses whether they have any db or not """
    title = _("has database")
    parameter_name = 'has_database'
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(databases__isnull=False)
        elif self.value() == 'False':
            return queryset.filter(databases__isnull=True)
        return queryset
