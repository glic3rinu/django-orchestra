from django.contrib import admin

from .models import Server, ScriptLog


admin.site.register(Server)
admin.site.register(ScriptLog)
