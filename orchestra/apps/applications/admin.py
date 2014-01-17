from django.contrib import admin

from .models import Application, Installation


class InstallationInline(admin.TabularInline):
    model = Installation


class ApplicationAdmin(admin.ModelAdmin):
    inlines = [InstallationInline]


admin.site.register(Application, ApplicationAdmin)
