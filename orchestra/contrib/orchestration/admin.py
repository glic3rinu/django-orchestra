from django.contrib import admin, messages
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin, ChangeViewActionsMixin
from orchestra.admin.utils import admin_link, admin_date, admin_colored, display_mono, display_code
from orchestra.plugins.admin import display_plugin_field

from . import settings, helpers
from .actions import retry_backend, orchestrate
from .backends import ServiceBackend
from .forms import RouteForm
from .models import Server, Route, BackendLog, BackendOperation
from .utils import retrieve_state
from .widgets import RouteBackendSelect


STATE_COLORS = {
    BackendLog.RECEIVED: 'darkorange',
    BackendLog.TIMEOUT: 'red',
    BackendLog.STARTED: 'blue',
    BackendLog.SUCCESS: 'green',
    BackendLog.FAILURE: 'red',
    BackendLog.ERROR: 'red',
    BackendLog.REVOKED: 'magenta',
    BackendLog.NOTHING: 'green',
}


class RouteAdmin(ExtendedModelAdmin):
    list_display = (
        'display_backend', 'host', 'match', 'display_model', 'display_actions', 'async',
        'is_active'
    )
    list_editable = ('host', 'match', 'async', 'is_active')
    list_filter = ('host', 'is_active', 'async', 'backend')
    list_prefetch_related = ('host',)
    ordering = ('backend',)
    add_fields = ('backend', 'host', 'match', 'async', 'is_active')
    change_form = RouteForm
    actions = (orchestrate,)
    change_view_actions = actions
    
    BACKEND_HELP_TEXT = helpers.get_backends_help_text(ServiceBackend.get_backends())
    DEFAULT_MATCH = {
        backend.get_name(): backend.default_route_match for backend in ServiceBackend.get_backends()
    }
    
    display_backend = display_plugin_field('backend')
    
    def display_model(self, route):
        try:
            return escape(route.backend_class.model)
        except KeyError:
            return "<span style='color: red;'>NOT AVAILABLE</span>"
    display_model.short_description = _("model")
    display_model.allow_tags = True
    
    def display_actions(self, route):
        try:
            return '<br>'.join(route.backend_class.get_actions())
        except KeyError:
            return "<span style='color: red;'>NOT AVAILABLE</span>"
    display_actions.short_description = _("actions")
    display_actions.allow_tags = True
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Provides dynamic help text on backend form field """
        if db_field.name == 'backend':
            kwargs['widget'] = RouteBackendSelect(
                'this.id', self.BACKEND_HELP_TEXT, self.DEFAULT_MATCH)
        field =  super(RouteAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'host':
            # Cache host choices
            request = kwargs['request']
            choices = getattr(request, '_host_choices_cache', None)
            if choices is None:
                request._host_choices_cache = choices = list(field.choices)
            field.choices = choices
        return field
    
    def get_form(self, request, obj=None, **kwargs):
        """ Include dynamic help text for existing objects """
        form = super(RouteAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['backend'].help_text = self.BACKEND_HELP_TEXT.get(obj.backend, '')
        return form
    
    def show_orchestration_disabled(self, request):
        if settings.ORCHESTRATION_DISABLE_EXECUTION:
            msg = _("Orchestration execution is disabled by <tt>ORCHESTRATION_DISABLE_EXECUTION</tt> setting.")
            self.message_user(request, mark_safe(msg), messages.WARNING)
    
    def changelist_view(self, request, extra_context=None):
        self.show_orchestration_disabled(request)
        return super(RouteAdmin, self).changelist_view(request, extra_context)
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        self.show_orchestration_disabled(request)
        return super(RouteAdmin, self).changeform_view(
            request, object_id, form_url, extra_context)


class BackendOperationInline(admin.TabularInline):
    model = BackendOperation
    fields = ('action', 'instance_link')
    readonly_fields = ('action', 'instance_link')
    extra = 0
    can_delete = False
    
    class Media:
        css = {
            'all': ('orchestra/css/hide-inline-id.css',)
        }
    
    def instance_link(self, operation):
        link = admin_link('instance')(self, operation)
        if link == '---':
            return _("Deleted {0}").format(operation.instance_repr or '-'.join(
                (escape(operation.content_type), escape(operation.object_id))))
        return link
    instance_link.allow_tags = True
    instance_link.short_description = _("Instance")
    
    def has_add_permission(self, *args, **kwargs):
        return False
    
    def get_queryset(self, request):
        queryset = super(BackendOperationInline, self).get_queryset(request)
        return queryset.prefetch_related('instance')


class BackendLogAdmin(ChangeViewActionsMixin, admin.ModelAdmin):
    list_display = (
        'id', 'backend', 'server_link', 'display_state', 'exit_code',
        'display_created', 'execution_time',
    )
    list_display_links = ('id', 'backend')
    list_filter = ('state', 'server', 'backend', 'operations__action')
    search_fields = ('script',)
    date_hierarchy = 'created_at'
    inlines = (BackendOperationInline,)
    fields = (
        'backend', 'server_link', 'state', 'display_script', 'mono_stdout',
        'mono_stderr', 'mono_traceback', 'exit_code', 'task_id', 'display_created',
        'execution_time'
    )
    readonly_fields = fields
    actions = (retry_backend,)
    change_view_actions = actions
    
    server_link = admin_link('server')
    display_created = admin_date('created_at', short_description=_("Created"))
    display_state = admin_colored('state', colors=STATE_COLORS)
    display_script = display_code('script')
    mono_stdout = display_mono('stdout')
    mono_stderr = display_mono('stderr')
    mono_traceback = display_mono('traceback')
    
    class Media:
        css = {
            'all': ('orchestra/css/pygments/github.css',)
        }
    
    def get_queryset(self, request):
        """ Order by structured name and imporve performance """
        qs = super(BackendLogAdmin, self).get_queryset(request)
        return qs.select_related('server').defer('script', 'stdout')
    
    def has_add_permission(self, *args, **kwargs):
        return False


class ServerAdmin(ExtendedModelAdmin):
    list_display = ('name', 'address', 'os', 'display_ping', 'display_uptime')
    list_filter = ('os',)
    actions = (orchestrate,)
    change_view_actions = actions
    
    def display_ping(self, instance):
        return self._remote_state[instance.pk][0]
    display_ping.short_description = _("Ping")
    display_ping.allow_tags = True
    
    def display_uptime(self, instance):
        return self._remote_state[instance.pk][1]
    display_uptime.short_description = _("Uptime")
    display_uptime.allow_tags = True
    
    def get_queryset(self, request):
        """ Order by structured name and imporve performance """
        qs = super(ServerAdmin, self).get_queryset(request)
        if request.method == 'GET' and request.resolver_match.func.__name__ == 'changelist_view':
            self._remote_state = retrieve_state(qs)
        return qs

admin.site.register(Server, ServerAdmin)
admin.site.register(BackendLog, BackendLogAdmin)
admin.site.register(Route, RouteAdmin)
