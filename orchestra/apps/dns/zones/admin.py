from django.contrib import admin

from .models import Domain, Record


class RecordInline(admin.TabularInline):
    model = Record


class DomainAdmin(admin.ModelAdmin):
    inlines = [RecordInline]

admin.site.register(Domain, DomainAdmin)
