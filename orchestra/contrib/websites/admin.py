from django import forms
from django.contrib import admin
from django.core.urlresolvers import resolve
from django.db.models import Q
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.actions import disable, enable
from orchestra.admin.utils import admin_link, change_url
from orchestra.contrib.accounts.actions import list_accounts
from orchestra.contrib.accounts.admin import AccountAdminMixin, SelectAccountAdminMixin
from orchestra.contrib.accounts.filters import IsActiveListFilter
from orchestra.forms.widgets import DynamicHelpTextSelect
from orchestra.utils.html import get_on_site_link

from .directives import SiteDirective
from .filters import HasWebAppsListFilter, HasDomainsFilter
from .forms import WebsiteAdminForm, WebsiteDirectiveInlineFormSet
from .models import Content, Website, WebsiteDirective


class WebsiteDirectiveInline(admin.TabularInline):
    model = WebsiteDirective
    formset = WebsiteDirectiveInlineFormSet
    extra = 1
    
    DIRECTIVES_HELP_TEXT = {
        op.name: force_text(op.help_text) for op in SiteDirective.get_plugins()
    }
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'value':
            kwargs['widget'] = forms.TextInput(attrs={'size':'100'})
        if db_field.name == 'name':
            # Help text based on select widget
            target = 'this.id.replace("name", "value")'
            kwargs['widget'] = DynamicHelpTextSelect(target, self.DIRECTIVES_HELP_TEXT)
        return super(WebsiteDirectiveInline, self).formfield_for_dbfield(db_field, **kwargs)


class ContentInline(AccountAdminMixin, admin.TabularInline):
    model = Content
    extra = 1
    fields = ('webapp', 'webapp_link', 'webapp_type', 'path')
    readonly_fields = ('webapp_link', 'webapp_type')
    filter_by_account_fields = ['webapp']
    
    webapp_link = admin_link('webapp', popup=True)
    webapp_link.short_description = _("Web App")
    
    def webapp_type(self, content):
        if not content.pk:
            return ''
        return content.webapp.get_type_display()
    webapp_type.short_description = _("Web App type")


class WebsiteAdmin(SelectAccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'name', 'display_domains', 'display_webapps', 'account_link', 'display_active'
    )
    list_filter = (
        'protocol', IsActiveListFilter, HasWebAppsListFilter, HasDomainsFilter
    )
    change_readonly_fields = ('name',)
    inlines = (ContentInline, WebsiteDirectiveInline)
    filter_horizontal = ['domains']
    fieldsets = (
        (None, {
            'classes': ('extrapretty',),
            'fields': ('account_link', 'name', 'protocol', 'target_server', 'domains', 'is_active', 'comments'),
        }),
    )
    form = WebsiteAdminForm
    filter_by_account_fields = ['domains']
    list_prefetch_related = ('domains', 'content_set__webapp')
    search_fields = ('name', 'account__username', 'domains__name', 'content__webapp__name')
    actions = (disable, enable, list_accounts)
    
    def display_domains(self, website):
        domains = []
        for domain in website.domains.all():
            url = '%s://%s' % (website.get_protocol(), domain)
            domains.append('<a href="%s">%s</a>' % (url, url))
        return '<br>'.join(domains)
    display_domains.short_description = _("domains")
    display_domains.allow_tags = True
    display_domains.admin_order_field = 'domains'
    
    def display_webapps(self, website):
        webapps = []
        for content in website.content_set.all():
            site_link = get_on_site_link(content.get_absolute_url())
            webapp = content.webapp
            detail = _("Edit Webapp") + ' ' + webapp.get_type_display()
            try:
                detail += ' ' + webapp.type_instance.get_detail()
            except KeyError:
                pass
            url = change_url(webapp)
            name = "%s on %s" % (webapp.name, content.path or '/')
            webapps.append('<a href="%s" title="%s">%s %s</a>' % (url, detail, name, site_link))
        return '<br>'.join(webapps)
    display_webapps.allow_tags = True
    display_webapps.short_description = _("Web apps")
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Exclude domains with exhausted ports
        has to be done here, on the form doesn't work because of filter_by_account_fields
        """
        formfield = super(WebsiteAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'domains':
            qset = Q(
                Q(websites__protocol=Website.HTTPS_ONLY) |
                Q(websites__protocol=Website.HTTP_AND_HTTPS) | Q(
                    Q(websites__protocol=Website.HTTP) & Q(websites__protocol=Website.HTTPS)
                )
            )
            args = resolve(kwargs['request'].path).args
            if args:
                object_id = args[0]
                qset = Q(qset & ~Q(websites__pk=object_id))
            formfield.queryset = formfield.queryset.exclude(qset)
        return formfield
    
    def _create_formsets(self, request, obj, change):
        """ bind contents formset to directive formset for unique location cross-validation """
        formsets, inline_instances = super(WebsiteAdmin, self)._create_formsets(request, obj, change)
        if request.method == 'POST':
            contents, directives = formsets
            directives.content_formset = contents
        return formsets, inline_instances


admin.site.register(Website, WebsiteAdmin)
