from django import forms
from django.contrib import admin
from django.core.urlresolvers import resolve
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import admin_link, change_url
from orchestra.apps.accounts.admin import AccountAdminMixin, SelectAccountAdminMixin
from orchestra.forms.widgets import DynamicHelpTextSelect

from . import settings
from .directives import SiteDirective
from .forms import WebsiteAdminForm
from .models import Content, Website, Directive


class DirectiveInline(admin.TabularInline):
    model = Directive
    extra = 1
    
    DIRECTIVES_HELP_TEXT = {
        op.name: str(unicode(op.help_text)) for op in SiteDirective.get_plugins()
    }
    
#    class Media:
#        css = {
#            'all': ('orchestra/css/hide-inline-id.css',)
#        }
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'value':
            kwargs['widget'] = forms.TextInput(attrs={'size':'100'})
        if db_field.name == 'name':
            # Help text based on select widget
            kwargs['widget'] = DynamicHelpTextSelect(
                'this.id.replace("name", "value")', self.DIECTIVES_HELP_TEXT
            )
        return super(DirectiveInline, self).formfield_for_dbfield(db_field, **kwargs)


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
    list_display = ('name', 'display_domains', 'display_webapps', 'account_link')
    list_filter = ('port', 'is_active')
    change_readonly_fields = ('name',)
    inlines = [ContentInline, DirectiveInline]
    filter_horizontal = ['domains']
    fieldsets = (
        (None, {
            'classes': ('extrapretty',),
            'fields': ('account_link', 'name', 'port', 'domains', 'is_active'),
        }),
    )
    form = WebsiteAdminForm
    filter_by_account_fields = ['domains']
    list_prefetch_related = ('domains', 'contents__webapp')
    search_fields = ('name', 'account__username', 'domains__name')
    
    def display_domains(self, website):
        domains = []
        for domain in website.domains.all():
            url = '%s://%s' % (website.protocol, domain)
            domains.append('<a href="%s">%s</a>' % (url, url))
        return '<br>'.join(domains)
    display_domains.short_description = _("domains")
    display_domains.allow_tags = True
    display_domains.admin_order_field = 'domains'
    
    def display_webapps(self, website):
        webapps = []
        for content in website.contents.all():
            webapp = content.webapp
            url = change_url(webapp)
            name = "%s on %s" % (webapp.get_type_display(), content.path)
            webapps.append('<a href="%s">%s</a>' % (url, name))
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
            qset = Q()
            for port, __ in settings.WEBSITES_PORT_CHOICES:
                qset = qset & Q(websites__port=port)
            args = resolve(kwargs['request'].path).args
            if args:
                object_id = args[0]
                qset = Q(qset & ~Q(websites__pk=object_id))
            formfield.queryset = formfield.queryset.exclude(qset)
        return formfield


admin.site.register(Website, WebsiteAdmin)
