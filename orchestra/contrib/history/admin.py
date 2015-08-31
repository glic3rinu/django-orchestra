from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.http import HttpResponseRedirect
from django.contrib.admin.utils import unquote

from orchestra.admin.utils import admin_link, admin_date


class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'display_action_time', 'user_link',
    )
    list_filter = ('action_flag', 'content_type',)
    date_hierarchy = 'action_time'
    search_fields = ('object_repr', 'change_message')
    fields = (
        'user_link', 'content_object_link', 'display_action_time', 'display_action', 'change_message'
    )
    readonly_fields = (
        'user_link', 'content_object_link', 'display_action_time', 'display_action',
    )
    actions = None
    
    user_link = admin_link('user')
    display_action_time = admin_date('action_time', short_description=_("Time"))
    
    def display_action(self, log):
        if log.is_addition():
            return _("Added")
        elif log.is_change():
            return _("Changed")
        return _("Deleted")
    display_action.short_description = _("Action")
    display_action.admin_order_field = 'action_flag'
    
    def content_object_link(self, log):
        ct = log.content_type
        try:
            url = reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=(log.object_id,))
        except NoReverseMatch:
            return log.object_repr
        return '<a href="%s">%s</a>' % (url, log.object_repr)
    content_object_link.short_description = _("Content object")
    content_object_link.admin_order_field = 'object_repr'
    content_object_link.allow_tags = True
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """ Add rel_opts and object to context """
        context = {}
        if 'edit' in request.GET.urlencode():
            obj = self.get_object(request, unquote(object_id))
            context = {
                'rel_opts': obj.content_type.model_class()._meta,
                'object': obj,
            }
        context.update(extra_context or {})
        return super(LogEntryAdmin, self).changeform_view(request, object_id, form_url, extra_context=context)

    def response_change(self, request, obj):
        """ save and continue preserve edit query string """
        response = super(LogEntryAdmin, self).response_change(request, obj)
        if 'edit' in request.GET.urlencode() and 'edit' not in response.url:
            return HttpResponseRedirect(response.url + '?edit=True')
        return response
    
    def response_post_save_change(self, request, obj):
        """ save redirect to object history """
        if 'edit' in request.GET.urlencode():
            opts = obj.content_type.model_class()._meta
            post_url = reverse('admin:%s_%s_history' % (opts.app_label, opts.model_name), args=(obj.object_id,))
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, post_url)
            return HttpResponseRedirect(post_url)
        return super(LogEntryAdmin, self).response_post_save_change(request, obj)
    
    def has_add_permission(self, *args, **kwargs):
        return False
    
    def has_delete_permission(self, *args, **kwargs):
        return False
    
    def log_addition(self, *args, **kwargs):
        pass
    
    def log_change(self, *args, **kwargs):
        pass
    
    def log_deletion(self, *args, **kwargs):
        pass


admin.site.register(admin.models.LogEntry, LogEntryAdmin)
