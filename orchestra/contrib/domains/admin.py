from django.contrib import admin
from django.db.models.functions import Concat, Coalesce
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import admin_link, change_url
from orchestra.contrib.accounts.actions import list_accounts
from orchestra.contrib.accounts.admin import AccountAdminMixin
from orchestra.utils import apps
from orchestra.utils.html import get_on_site_link

from .actions import view_zone, edit_records, set_soa
from .filters import TopDomainListFilter
from .forms import RecordForm, RecordInlineFormSet, BatchDomainCreationAdminForm
from .models import Domain, Record


class RecordInline(admin.TabularInline):
    model = Record
    form = RecordForm
    formset = RecordInlineFormSet
    verbose_name_plural = _("Extra records")


class DomainInline(admin.TabularInline):
    model = Domain
    fields = ('domain_link', 'display_records', 'account_link')
    readonly_fields = ('domain_link', 'display_records', 'account_link')
    extra = 0
    verbose_name_plural = _("Subdomains")
    
    domain_link = admin_link('__str__')
    domain_link.short_description = _("Name")
    account_link = admin_link('account')
    
    def display_records(self, domain):
        return ', '.join([record.type for record in domain.records.all()])
    display_records.short_description = _("Declared records")
    
    def has_add_permission(self, *args, **kwargs):
        return False
    
    def get_queryset(self, request):
        """ Order by structured name and imporve performance """
        qs = super(DomainInline, self).get_queryset(request)
        return qs.select_related('account').prefetch_related('records')


class DomainAdmin(AccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'structured_name', 'display_is_top', 'display_websites', 'account_link'
    )
    add_fields = ('name', 'account')
    fields = ('name', 'account_link')
    readonly_fields = ('account_link', 'top_link',)
    inlines = (RecordInline, DomainInline)
    list_filter = (TopDomainListFilter,)
    change_readonly_fields = ('name', 'serial')
    search_fields = ('name', 'account__username', 'records__value')
    add_form = BatchDomainCreationAdminForm
    actions = (edit_records, set_soa, list_accounts)
    change_view_actions = (view_zone, edit_records)
    
    top_link = admin_link('top')
    
    def structured_name(self, domain):
        if domain.is_top:
            return domain.name
        return '&nbsp;'*4 + domain.name
    structured_name.short_description = _("name")
    structured_name.allow_tags = True
    structured_name.admin_order_field = 'structured_name'
    
    def display_is_top(self, domain):
        return domain.is_top
    display_is_top.short_description = _("Is top")
    display_is_top.boolean = True
    display_is_top.admin_order_field = 'top'
    
    def display_websites(self, domain):
        if apps.isinstalled('orchestra.contrib.websites'):
            websites = domain.websites.all()
            if websites:
                links = []
                for website in websites:
                    site_link = get_on_site_link(website.get_absolute_url())
                    admin_url = change_url(website)
                    link = '<a href="%s">%s %s</a>' % (admin_url, website.name, site_link)
                    links.append(link)
                return '<br>'.join(links)
        site_link = get_on_site_link('http://%s' % domain.name)
        return _("No website %s") % site_link
    display_websites.admin_order_field = 'websites__name'
    display_websites.short_description = _("Websites")
    display_websites.allow_tags = True
    
    def get_fieldsets(self, request, obj=None):
        """ Add SOA fields when domain is top """
        fieldsets = super(DomainAdmin, self).get_fieldsets(request, obj)
        if obj:
            if obj.is_top:
                fieldsets += (
                    (_("SOA"), {
                        'classes': ('collapse',),
                        'fields': ('serial', 'refresh', 'retry', 'expire', 'min_ttl'),
                    }),
                )
            else:
                existing = fieldsets[0][1]['fields']
                if 'top_link' not in existing:
                    fieldsets[0][1]['fields'].insert(2, 'top_link')
        return fieldsets
    
    def get_inline_instances(self, request, obj=None):
        inlines = super(DomainAdmin, self).get_inline_instances(request, obj)
        if not obj or not obj.is_top:
            return [inline for inline in inlines if type(inline) != DomainInline]
        return inlines
    
    def get_queryset(self, request):
        """ Order by structured name and imporve performance """
        qs = super(DomainAdmin, self).get_queryset(request)
        qs = qs.select_related('top', 'account')
        if request.method == 'GET':
            qs = qs.annotate(
                structured_id=Coalesce('top__id', 'id'),
                structured_name=Concat('top__name', 'name')
            ).order_by('-structured_id', 'structured_name')
        if apps.isinstalled('orchestra.contrib.websites'):
            qs = qs.prefetch_related('websites')
        return qs
    
    def save_model(self, request, obj, form, change):
        """ batch domain creation support """
        super(DomainAdmin, self).save_model(request, obj, form, change)
        self.extra_domains = []
        if not change:
            for name in form.extra_names:
                domain = Domain.objects.create(name=name, account_id=obj.account_id)
                self.extra_domains.append(domain)
    
    def save_related(self, request, form, formsets, change):
        """ batch domain creation support """
        super(DomainAdmin, self).save_related(request, form, formsets, change)
        if not change:
            # Clone records to extra_domains, if any
            for formset in formsets:
                if formset.model is Record:
                    for domain in self.extra_domains:
                        # Reset pk value of the record instances to force creation of new ones
                        for record_form in formset.forms:
                            record = record_form.instance
                            if record.pk:
                                record.pk = None
                        formset.instance = domain
                        form.instance = domain
                        self.save_formset(request, form, formset, change)


admin.site.register(Domain, DomainAdmin)
