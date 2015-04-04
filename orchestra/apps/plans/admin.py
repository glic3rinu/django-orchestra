from django.contrib import admin

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import insertattr
from orchestra.apps.accounts.admin import AccountAdminMixin
from orchestra.apps.services.models import Service

from .models import Plan, ContractedPlan, Rate


class RateInline(admin.TabularInline):
    model = Rate
    ordering = ('plan', 'quantity')


class PlanAdmin(ExtendedModelAdmin):
    list_display = ('name', 'is_default', 'is_combinable', 'allow_multiple')
    list_filter = ('is_default', 'is_combinable', 'allow_multiple')
    fields = ('verbose_name', 'name', 'is_default', 'is_combinable', 'allow_multiple')
    prepopulated_fields = {
        'name': ('verbose_name',)
    }
    change_readonly_fields = ('name',)
    inlines = [RateInline]


class ContractedPlanAdmin(AccountAdminMixin, admin.ModelAdmin):
    list_display = ('plan', 'account_link')
    list_filter = ('plan__name',)


admin.site.register(Plan, PlanAdmin)
admin.site.register(ContractedPlan, ContractedPlanAdmin)

insertattr(Service, 'inlines', RateInline)
