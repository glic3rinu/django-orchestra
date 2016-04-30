import re

from django.conf.urls import url
from django.contrib.admin.utils import unquote
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import wrap_admin_view


class SelectPluginAdminMixin(object):
    plugin = None
    plugin_field = None
    plugin_title = None
    
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            try:
                plugin = getattr(obj, '%s_instance' % self.plugin_field)
            except KeyError:
                plugin_name = getattr(obj, self.plugin_field)
                raise KeyError(_("Plugin '%s' is not available.") % plugin_name)
            else:
                self.form = getattr(plugin, 'get_change_form', plugin.get_form)()
        else:
            plugin = self.plugin.get(self.plugin_value)()
            self.form = plugin.get_form()
        self.plugin_instance = plugin
        return super(SelectPluginAdminMixin, self).get_form(request, obj, **kwargs)
    
    def get_fields(self, request, obj=None):
        """ Try to maintain original field ordering """
        fields = super(SelectPluginAdminMixin, self).get_fields(request, obj)
        head_fields = list(self.get_readonly_fields(request, obj))
        head, tail = [], []
        for field in fields:
            if field in head_fields:
                head.append(field)
            else:
                tail.append(field)
        return head + tail
    
    def get_urls(self):
        """ Hooks select account url """
        urls = super(SelectPluginAdminMixin, self).get_urls()
        opts = self.model._meta
        info = opts.app_label, opts.model_name
        select_urls = [
            url("select-plugin/$",
                wrap_admin_view(self, self.select_plugin_view),
                name='%s_%s_select_plugin' % info),
        ]
        return select_urls + urls
    
    def select_plugin_view(self, request):
        opts = self.model._meta
        context = {
            'plugin_title': self.plugin_title or 'Plugins',
            'opts': opts,
            'app_label': opts.app_label,
            'field': self.plugin_field,
            'field_name': opts.get_field(self.plugin_field).verbose_name,
            'plugin': self.plugin,
            'plugins': self.plugin.get_plugins(),
        }
        template = 'admin/plugins/select_plugin.html'
        return render(request, template, context)
    
    def get_plugin_value(self, request):
        plugin_value = request.GET.get(self.plugin_field) or request.POST.get(self.plugin_field)
        if not plugin_value and request.method == 'POST':
            # HACK baceuse django add_preserved_filters removes extising queryargs
            value = re.search(r"%s=([^&^']+)[&']" % self.plugin_field,
                request.META.get('HTTP_REFERER', ''))
            if value:
                plugin_value = value.groups()[0]
        return plugin_value
    
    def add_view(self, request, form_url='', extra_context=None):
        """ Redirects to select account view if required """
        if request.user.is_superuser:
            plugin_value = self.get_plugin_value(request)
            if plugin_value or len(self.plugin.get_plugins()) == 1:
                self.plugin_value = plugin_value
                if not plugin_value:
                    self.plugin_value = self.plugin.get_plugins()[0].get_name()
                plugin = self.plugin.get(self.plugin_value)
                context = {
                    'title': _("Add new %s") % plugin.verbose_name,
                }
                context.update(extra_context or {})
                return super(SelectPluginAdminMixin, self).add_view(
                    request, form_url=form_url, extra_context=context)
        return redirect('./select-plugin/?%s' % request.META['QUERY_STRING'])
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        try:
            verbose = getattr(obj, '%s_class' % self.plugin_field).verbose_name
        except KeyError:
            raise KeyError(_("Plugin '%s' is not available.") % getattr(obj, self.plugin_field))
        context = {
            'title': _("Change %s") % verbose,
        }
        context.update(extra_context or {})
        return super(SelectPluginAdminMixin, self).change_view(
            request, object_id, form_url=form_url, extra_context=context)
    
    def save_model(self, request, obj, form, change):
        if not change:
            setattr(obj, self.plugin_field, self.plugin_value)
        obj.save()


def display_plugin_field(field_name):
    def inner(modeladmin, obj, field_name=field_name):
        try:
            getattr(obj, '%s_class' % field_name)
        except KeyError:
            value = getattr(obj, field_name)
            return "<span style='color:red;' title='Not available'>%s</span>" % value
        return getattr(obj, 'get_%s_display' % field_name)()
    inner.short_description = field_name
    inner.admin_order_field = field_name
    inner.allow_tags = True
    return inner
