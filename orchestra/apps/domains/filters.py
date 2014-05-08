from django.contrib.admin import SimpleListFilter
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _


class TopDomainListFilter(SimpleListFilter):
    """ Filter Nodes by group according to request.user """
    title = _("Top domains")
    parameter_name = 'top_domain'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("Top domains")),
            ('False', _("All")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(top__isnull=True)
    
    def choices(self, cl):
        """ Enable default selection different than All """
        for lookup, title in self.lookup_choices:
            title = title._proxy____args[0]
            selected = self.value() == force_text(lookup)
            if not selected and title == "Top domains" and self.value() is None:
                selected = True
            # end of workaround
            yield {
                'selected': selected,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }
