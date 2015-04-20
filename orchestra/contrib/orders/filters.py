from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _


class ActiveOrderListFilter(SimpleListFilter):
    """ Filter tickets by created_by according to request.user """
    title = _("is active")
    parameter_name = 'is_active'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("Active")),
            ('False', _("Inactive")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.active()
        elif self.value() == 'False':
            return queryset.inactive()
        return queryset


class BilledOrderListFilter(SimpleListFilter):
    """ Filter tickets by created_by according to request.user """
    title = _("billed")
    parameter_name = 'pending'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', _("Billed")),
            ('no', _("Not billed")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(billed_until__isnull=False,
                    billed_until__gte=timezone.now())
        elif self.value() == 'no':
            return queryset.filter(
                Q(billed_until__isnull=True) |
                Q(billed_until__lt=timezone.now())
            )
        return queryset


class IgnoreOrderListFilter(SimpleListFilter):
    """ Filter Nodes by group according to request.user """
    title = _("Ignore")
    parameter_name = 'ignore'
    
    def lookups(self, request, model_admin):
        return (
            ('0', _("Not ignored")),
            ('1', _("Ignored")),
            ('2', _("All")),
            
        )
    
    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(ignore=False)
        elif self.value() == '1':
            return queryset.filter(ignore=True)
        return queryset
    
    def choices(self, cl):
        """ Enable default selection different than All """
        for lookup, title in self.lookup_choices:
            title = title._proxy____args[0]
            selected = self.value() == force_text(lookup)
            if not selected and title == "Not ignored" and self.value() is None:
                selected = True
            # end of workaround
            yield {
                'selected': selected,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }
