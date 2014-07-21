from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.core.urlresolvers import reverse
from django.db.models import F
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ChangeListDefaultFilter, ExtendedModelAdmin
from orchestra.admin.utils import wrap_admin_view, admin_link
from orchestra.apps.accounts.admin import AccountAdminMixin
from orchestra.utils import apps

from .forms import RecordInlineFormSet, DomainAdminForm
from .filters import TopDomainListFilter
from .models import Domain, Record


class RecordInline(admin.TabularInline):
    model = Record
    formset = RecordInlineFormSet
    verbose_name_plural = _("Extra records")
    
    class Media:
        css = {
            'all': ('orchestra/css/hide-inline-id.css',)
        }
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'value':
            kwargs['widget'] = forms.TextInput(attrs={'size':'100'})
        return super(RecordInline, self).formfield_for_dbfield(db_field, **kwargs)


class DomainInline(admin.TabularInline):
    model = Domain
    fields = ('domain_link',)
    readonly_fields = ('domain_link',)
    extra = 0
    verbose_name_plural = _("Subdomains")
    
    domain_link = admin_link()
    domain_link.short_description = _("Name")
    
    def has_add_permission(self, *args, **kwargs):
        return False


class DomainAdmin(ChangeListDefaultFilter, AccountAdminMixin, ExtendedModelAdmin):
    fields = ('name', 'account')
    list_display = (
        'structured_name', 'display_is_top', 'websites', 'account_link'
    )
    inlines = [RecordInline, DomainInline]
    list_filter = [TopDomainListFilter]
    change_readonly_fields = ('name',)
    search_fields = ['name', 'account__user__username']
    default_changelist_filters = (('top_domain', 'True'),)
    form = DomainAdminForm
    
    def structured_name(self, domain):
        if not domain.is_top:
            return '&nbsp;'*4 + domain.name
        return domain.name
    structured_name.short_description = _("name")
    structured_name.allow_tags = True
    structured_name.admin_order_field = 'structured_name'
    
    def display_is_top(self, domain):
        return domain.is_top
    display_is_top.boolean = True
    display_is_top.admin_order_field = 'top'
    
    def websites(self, domain):
        if apps.isinstalled('orchestra.apps.websites'):
            webs = domain.websites.all()
            if webs:
                links = []
                for web in webs:
                    url = reverse('admin:websites_website_change', args=(web.pk,))
                    links.append('<a href="%s">%s</a>' % (url, web.name))
                return '<br>'.join(links)
        return _("No website")
    websites.admin_order_field = 'websites__name'
    websites.short_description = _("Websites")
    websites.allow_tags = True
    
    def get_urls(self):
        """ Returns the additional urls for the change view links """
        urls = super(DomainAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        urls = patterns("",
            url('^(\d+)/view-zone/$',
                wrap_admin_view(self, self.view_zone_view),
                name='domains_domain_view_zone')
        ) + urls
        return urls
    
    def view_zone_view(self, request, object_id):
        zone = self.get_object(request, unquote(object_id))
        context = {
            'opts': self.model._meta,
            'object': zone,
            'title': _("%s zone content") % zone.origin.name
        }
        return TemplateResponse(request, 'admin/domains/domain/view_zone.html',
            context)
    
    def get_queryset(self, request):
        """ Order by structured name and imporve performance """
        qs = super(DomainAdmin, self).get_queryset(request)
        qs = qs.select_related('top', 'account__user')
#        qs = qs.select_related('top')
        # For some reason if we do this we know for sure that join table will be called T4
        __ = str(qs.query)
        qs = qs.extra(
            select={'structured_name': 'CONCAT(T4.name, domains_domain.name)'},
        ).order_by('structured_name')
        if apps.isinstalled('orchestra.apps.websites'):
            qs = qs.prefetch_related('websites')
        return qs


admin.site.register(Domain, DomainAdmin)
