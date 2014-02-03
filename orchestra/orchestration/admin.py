from django.contrib import admin
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from orchestra.utils.html import monospace_format

from .models import Server, ScriptLog


class ScriptLogAdmin(admin.ModelAdmin):
    fields = [
        'state', 'server', 'mono_script', 'mono_stdout', 'mono_stderr',
        'mono_traceback', 'exit_code', 'task_id'
    ]
    readonly_fields = [
        'state', 'server', 'mono_script', 'mono_stdout', 'mono_stderr',
        'mono_traceback', 'exit_code', 'task_id'
    ]
    
    def mono_script(self, instance):
        return monospace_format(escape(instance.script))
    mono_script.short_description = _("script")
    
    def mono_stdout(self, instance):
        return monospace_format(escape(instance.stdout))
    mono_stdout.short_description = _("stdout")
    
    def mono_stderr(self, instance):
        return monospace_format(escape(instance.stderr))
    mono_stderr.short_description = _("stderr")
    
    def mono_traceback(self, instance):
        return monospace_format(escape(instance.traceback))
    mono_traceback.short_description = _("traceback")


admin.site.register(Server)
admin.site.register(ScriptLog, ScriptLogAdmin)
