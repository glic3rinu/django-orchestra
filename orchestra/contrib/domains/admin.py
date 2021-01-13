from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.functions import Concat, Coalesce
from django.templatetags.static import static
from django.utils.translation import ugettext, ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import admin_link, change_url
from orchestra.contrib.accounts.actions import list_accounts
from orchestra.contrib.accounts.admin import AccountAdminMixin
from orchestra.utils import apps
from orchestra.utils.html import get_on_site_link

from . import settings
from .actions import view_zone, edit_records, set_soa
from .filters import TopDomainListFilter, HasWebsiteFilter, HasAddressFilter
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
        'structured_name', 'display_is_top', 'display_websites', 'display_addresses', 'account_link'
    )
    add_fields = ('name', 'account')
    fields = ('name', 'account_link', 'display_websites', 'display_addresses', 'dns2136_address_match_list')
    readonly_fields = (
        'account_link', 'top_link', 'display_websites', 'display_addresses', 'implicit_records'
    )
    inlines = (RecordInline, DomainInline)
    list_filter = (TopDomainListFilter, HasWebsiteFilter, HasAddressFilter)
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
                    title = _("Edit website")
                    link = '<a href="%s" title="%s">%s %s</a>' % (
                        admin_url, title, website.name, site_link)
                    links.append(link)
                return '<br>'.join(links)
            add_url = reverse('admin:websites_website_add')
            add_url += '?account=%i&domains=%i' % (domain.account_id, domain.pk)
            image = '<img src="%s"></img>' % static('orchestra/images/add.png')
            add_link = '<a href="%s" title="%s">%s</a>' % (
                add_url, _("Add website"), image
            )
            return _("No website %s") % (add_link)
        return '---'
    display_websites.admin_order_field = 'websites__name'
    display_websites.short_description = _("Websites")
    display_websites.allow_tags = True
    
    def display_addresses(self, domain):
        if apps.isinstalled('orchestra.contrib.mailboxes'):
            add_url = reverse('admin:mailboxes_address_add')
            add_url += '?account=%i&domain=%i' % (domain.account_id, domain.pk)
            image = '<img src="%s"></img>' % static('orchestra/images/add.png')
            add_link = '<a href="%s" title="%s">%s</a>' % (
                add_url, _("Add address"), image
            )
            addresses = domain.addresses.all()
            if addresses:
                url = reverse('admin:mailboxes_address_changelist')
                url += '?domain=%i' % addresses[0].domain_id
                title = '\n'.join([address.email for address in addresses])
                return '<a href="%s" title="%s">%s</a> %s' % (url, title, len(addresses), add_link)
            return _("No address %s") % (add_link)
        return '---'
    display_addresses.short_description = _("Addresses")
    display_addresses.admin_order_field = 'addresses__count'
    display_addresses.allow_tags = True
    
    def implicit_records(self, domain):
        defaults = []
        types = set(domain.records.values_list('type', flat=True))
        ttl = settings.DOMAINS_DEFAULT_TTL
        lines = []
        for record in domain.get_default_records():
            line = '{name} {ttl} IN {type} {value}'.format(
                name=domain.name,
                ttl=ttl,
                type=record.type,
                value=record.value
            )
            if not domain.record_is_implicit(record, types):
                line = '<strike>%s</strike>' % line
            if record.type is Record.SOA:
                lines.insert(0, line)
            else:
                lines.append(line)
        return '<br>'.join(lines)
    implicit_records.short_description = _("Implicit records")
    implicit_records.allow_tags = True
    
    def get_fieldsets(self, request, obj=None):
        """ Add SOA fields when domain is top """
        fieldsets = super(DomainAdmin, self).get_fieldsets(request, obj)
        if obj:
            fieldsets += (
                (_("Implicit records"), {
                    'classes': ('collapse',),
                    'fields': ('implicit_records',),
                }),
            )
            if obj.is_top:
                fieldsets += (
                    (_("SOA"), {
                        'classes': ('collapse',),
                        'description': _(
                            "SOA (Start of Authority) records are used to determine how the "
                            "zone propagates to the secondary nameservers."),
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
            qs = qs.prefetch_related('websites__domains')
        if apps.isinstalled('orchestra.contrib.mailboxes'):
            qs = qs.annotate(models.Count('addresses'))
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
