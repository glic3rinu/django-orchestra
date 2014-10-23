from django.contrib.admin import SimpleListFilter
from django.db.models import F
from django.utils.encoding import force_text
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
            return queryset.filter(account__main_systemuser_id=F('id'))
        if self.value() == 'False':
            return queryset.exclude(account__main_systemuser_id=F('id'))

