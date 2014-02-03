from django.contrib import admin

from .models import Route


class RouteAdmin(admin.ModelAdmin):
    list_display = ['id', 'backend', 'host', 'match', 'is_active']
    list_editable = ['backend', 'host', 'match', 'is_active']
    list_filter = ['backend', 'host', 'is_active']


admin.site.register(Route, RouteAdmin)
