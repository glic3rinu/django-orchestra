from django.contrib import admin

from .models import Application, Tenant


class TenantInline(admin.TabularInline):
    model = Tenant


class ApplicationAdmin(admin.ModelAdmin):
    inlines = [TenantInline]


admin.site.register(Application, ApplicationAdmin)
