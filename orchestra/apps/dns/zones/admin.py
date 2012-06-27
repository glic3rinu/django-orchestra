from common.forms import get_initial_form, get_initial_formset
from django.contrib import admin
from django.utils.functional import curry
from django.utils.translation import ugettext as _
from models import Zone, Record
import settings

class RecordInline(admin.TabularInline):
    model = Record
    extra = 1
    form = get_initial_form(Record)
    formset = get_initial_formset(form)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(RecordInline, self).get_formset(request, obj, **kwargs)
        if not obj:
            initial = settings.DNS_DEFAULT_DOMAIN_REGISTERS
            formset.__init__ = curry(formset.__init__, initial=initial)
        return formset


def domain_link(self):
    return '<a href="http://%s">http://%s</a>' % (self, self)
domain_link.short_description = _("Domain link")
domain_link.allow_tags = True


class ZoneAdmin(admin.ModelAdmin):
    list_display = ['origin', domain_link, ]
    fieldsets = ((None,     {'fields': (('origin',), 
                                        ('primary_ns', 'hostmaster_email'),
                                        )}),
        ('Optional Fields', {'classes': ('collapse',),
                             'fields': (('serial',),
                                        ('slave_refresh',),
                                        ('slave_retry',),
                                        ('slave_expiration',),
                                        ('min_caching_time'),)}),)
    inlines = [RecordInline,]


admin.site.register(Zone, ZoneAdmin)
