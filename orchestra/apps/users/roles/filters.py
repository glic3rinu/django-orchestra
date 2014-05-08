from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


def role_list_filter_factory(role):
    class RoleListFilter(SimpleListFilter):
        """ Filter Nodes by group according to request.user """
        title = _("has %s" % role.name)
        parameter_name = role.url_name
        
        def lookups(self, request, model_admin):
            return (
                ('True', _("Yes")),
                ('False', _("No")),
            )
        
        def queryset(self, request, queryset):
            if self.value() == 'True':
                return queryset.filter(**{ '%s__isnull' % role.name: False })
            if self.value() == 'False':
                return queryset.filter(**{ '%s__isnull' % role.name: True })
    
    return RoleListFilter
