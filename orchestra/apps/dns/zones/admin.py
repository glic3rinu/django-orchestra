from django.contrib import admin

from .forms import RecordInlineFormSet
from .models import Zone, Record


class RecordInline(admin.TabularInline):
    model = Record
    formset = RecordInlineFormSet


class ZoneAdmin(admin.ModelAdmin):
    inlines = [RecordInline]


admin.site.register(Zone, ZoneAdmin)
