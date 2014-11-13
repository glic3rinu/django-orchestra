from django.conf.urls import patterns, url
from django.contrib.admin.utils import unquote
from django.shortcuts import render, redirect
from django.utils.text import camel_case_to_spaces
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import wrap_admin_view
from orchestra.utils.functional import cached


class SelectPluginAdminMixin(object):
    plugin = None
    plugin_field = None
    
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = getattr(obj, '%s_class' % self.plugin_field)().get_form()
        else:
            self.form = self.plugin.get_plugin(self.plugin_value)().get_form()
        return super(SelectPluginAdminMixin, self).get_form(request, obj=obj, **kwargs)
    
    def get_urls(self):
        """ Hooks select account url """
        urls = super(SelectPluginAdminMixin, self).get_urls()
        opts = self.model._meta
        info = opts.app_label, opts.model_name
        select_urls = patterns("",
            url("/select-plugin/$",
                wrap_admin_view(self, self.select_plugin_view),
                name='%s_%s_select_plugin' % info),
        )
        return select_urls + urls 
    
    def select_plugin_view(self, request):
        opts = self.model._meta
        context = {
            'opts': opts,
            'app_label': opts.app_label,
            'field': self.plugin_field,
            'field_name': opts.get_field_by_name(self.plugin_field)[0].verbose_name,
            'plugin': self.plugin,
            'plugins': self.plugin.get_plugins(),
        }
        template = 'admin/plugins/select_plugin.html'
        return render(request, template, context)
    
    def add_view(self, request, form_url='', extra_context=None):
        """ Redirects to select account view if required """
        if request.user.is_superuser:
            plugin_value = request.GET.get(self.plugin_field) or request.POST.get(self.plugin_field)
            if plugin_value or len(self.plugin.get_plugins()) == 1:
                self.plugin_value = plugin_value
                if not plugin_value:
                    self.plugin_value = self.plugin.get_plugins()[0].get_name()
                context = {
                    'title': _("Add new %s") % camel_case_to_spaces(self.plugin_value),
                }
                context.update(extra_context or {})
                return super(SelectPluginAdminMixin, self).add_view(request, form_url=form_url,
                        extra_context=context)
        return redirect('./select-plugin/?%s' % request.META['QUERY_STRING'])
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        plugin_value = getattr(obj, self.plugin_field)
        context = {
            'title': _("Change %s") % camel_case_to_spaces(str(plugin_value)),
        }
        context.update(extra_context or {})
        return super(SelectPluginAdminMixin, self).change_view(request, object_id,
                form_url=form_url, extra_context=context)
    
    def save_model(self, request, obj, form, change):
        if not change:
            setattr(obj, self.plugin_field, self.plugin_value)
        obj.save()
