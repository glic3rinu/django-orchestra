from django.contrib import admin

from orchestra.admin.utils import insertattr
from orchestra.apps.accounts.admin import AccountAdminMixin
from orchestra.apps.orders.models import Service

from .models import Pack, Rate


class PackAdmin(AccountAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'account_link')
    list_filter = ('name',)


admin.site.register(Pack, PackAdmin)


class RateInline(admin.TabularInline):
    model = Rate
    ordering = ('pack', 'quantity')


insertattr(Service, 'inlines', RateInline)
