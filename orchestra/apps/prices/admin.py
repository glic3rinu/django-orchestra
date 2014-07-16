from django.contrib import admin

from orchestra.admin.utils import insertattr
from orchestra.apps.orders.models import Service

from .models import Pack, Rate


class PackAdmin(admin.ModelAdmin):
    pass

admin.site.register(Pack, PackAdmin)


class RateInline(admin.TabularInline):
    model = Rate
    ordering = ('pack', 'quantity')


insertattr(Service, 'inlines', RateInline)
