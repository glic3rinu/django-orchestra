from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import change_url
from orchestra.apps.accounts.admin import AccountAdminMixin
from orchestra.forms.widgets import DynamicHelpTextSelect
from orchestra.plugins.admin import SelectPluginAdminMixin

from . import settings
from .options import AppOption
from .types import AppType
from .models import WebApp, WebAppOption


class WebAppOptionInline(admin.TabularInline):
    model = WebAppOption
    extra = 1
    
    OPTIONS_HELP_TEXT = {
        op.name: str(unicode(op.help_text)) for op in AppOption.get_plugins()
    }
    
    class Media:
        css = {
            'all': ('orchestra/css/hide-inline-id.css',)
        }
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'value':
            kwargs['widget'] = forms.TextInput(attrs={'size':'100'})
        if db_field.name == 'name':
            if self.parent_object:
                plugin = self.parent_object.type_class
            else:
                request = kwargs['request']
                plugin = AppType.get(request.GET['type'])
            kwargs['choices'] = plugin.get_options_choices()
            # Help text based on select widget
            target = 'this.id.replace("name", "value")'
            kwargs['widget'] = DynamicHelpTextSelect(target, self.OPTIONS_HELP_TEXT)
        return super(WebAppOptionInline, self).formfield_for_dbfield(db_field, **kwargs)


class WebAppAdmin(SelectPluginAdminMixin, AccountAdminMixin, ExtendedModelAdmin):
    list_display = ('name', 'type', 'display_detail', 'display_websites', 'account_link')
    list_filter = ('type',)
    inlines = [WebAppOptionInline]
    readonly_fields = ('account_link', )
    change_readonly_fields = ('name', 'type', 'display_websites')
    search_fields = ('name', 'account__username', 'data', 'website__domains__name')
    list_prefetch_related = ('content_set__website',)
    plugin = AppType
    plugin_field = 'type'
    plugin_title = _("Web application type")
    
    def display_websites(self, webapp):
        websites = []
        for content in webapp.content_set.all():
            website = content.website
            url = change_url(website)
            name = "%s on %s" % (website.name, content.path)
            websites.append('<a href="%s">%s</a>' % (url, name))
        if not websites:
            add_url = reverse('admin:websites_website_add')
            add_url += '?account=%s' % webapp.account_id
            plus = '<strong style="color:green; font-size:12px">+</strong>'
            websites.append('<a href="%s">%s%s</a>' % (add_url, plus, ugettext("Add website")))
        return '<br>'.join(websites)
    display_websites.short_description = _("web sites")
    display_websites.allow_tags = True
    
    def display_detail(self, webapp):
        return webapp.type_instance.get_detail()
    display_detail.short_description = _("detail")
    
#    def formfield_for_dbfield(self, db_field, **kwargs):
#        """ Make value input widget bigger """
#        if db_field.name == 'type':
#            # Help text based on select widget
#            kwargs['widget'] = DynamicHelpTextSelect(
#                'this.id.replace("name", "value")', self.TYPE_HELP_TEXT
#            )
#            kwargs['help_text'] = self.TYPE_HELP_TEXT.get(db_field.default, '')
#        return super(WebAppAdmin, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.register(WebApp, WebAppAdmin)
