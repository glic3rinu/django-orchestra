from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import admin_link, change_url
from orchestra.apps.accounts.admin import AccountAdminMixin, SelectAccountAdminMixin

from . import settings
from .models import Content, Website, WebsiteOption


class WebsiteOptionInline(admin.TabularInline):
    model = WebsiteOption
    extra = 1
    
    OPTIONS_HELP_TEXT = {
        k: str(unicode(v[1])) if len(v) == 3 else ''
            for k, v in settings.WEBSITES_OPTIONS.iteritems()
    }
    
#    class Media:
#        css = {
#            'all': ('orchestra/css/hide-inline-id.css',)
#        }
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'value':
            kwargs['widget'] = forms.TextInput(attrs={'size':'100'})
        if db_field.name == 'name':
            # Help text based on select widget
            kwargs['widget'] = forms.Select(attrs={
                'onChange': """
                    siteoptions = %s;
                    valueelement = $("#"+this.id.replace("name", "value"));
                    valueelement.parent().find('p').remove();
                    valueelement.parent().append(
                        "<p class='help'>" + siteoptions[this.options[this.selectedIndex].value] + "</p>"
                    );
                """ % str(self.OPTIONS_HELP_TEXT),
            })
        return super(WebsiteOptionInline, self).formfield_for_dbfield(db_field, **kwargs)


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
    inlines = [ContentInline, WebsiteOptionInline]
    filter_horizontal = ['domains']
    fieldsets = (
        (None, {
            'classes': ('extrapretty',),
            'fields': ('account_link', 'name', 'port', 'domains', 'is_active'),
        }),
    )
    filter_by_account_fields = ['domains']
    prefetch_related = ('domains', 'content_set__webapp')
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
        for content in website.content_set.all():
            webapp = content.webapp
            url = change_url(webapp)
            name = "%s on %s" % (webapp.get_type_display(), content.path)
            webapps.append('<a href="%s">%s</a>' % (url, name))
        return '<br>'.join(webapps)
    display_webapps.allow_tags = True
    display_webapps.short_description = _("Web apps")
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'root':
            kwargs['widget'] = forms.TextInput(attrs={'size':'100'})
        return super(WebsiteAdmin, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(Website, WebsiteAdmin)
