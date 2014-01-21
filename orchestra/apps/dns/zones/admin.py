from django.contrib import admin

from .models import Zone, Record


class RecordInline(admin.TabularInline):
    model = Record


class ZoneAdmin(admin.ModelAdmin):
    inlines = [RecordInline]


admin.site.register(Zone, ZoneAdmin)
