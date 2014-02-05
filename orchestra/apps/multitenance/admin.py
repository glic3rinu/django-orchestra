from django.contrib import admin

from .models import Application, Tenant


class TenantAdmin(admin.ModelAdmin):
    pass


admin.site.register(Application)
admin.site.register(Tenant, TenantAdmin)
