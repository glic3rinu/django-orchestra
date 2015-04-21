from django.contrib import admin

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import insertattr
from orchestra.contrib.accounts.admin import AccountAdminMixin
from orchestra.contrib.services.models import Service

from .models import Plan, ContractedPlan, Rate


class RateInline(admin.TabularInline):
    model = Rate
    ordering = ('service', 'plan', 'quantity')


class PlanAdmin(ExtendedModelAdmin):
    list_display = ('name', 'is_default', 'is_combinable', 'allow_multiple', 'is_active')
    list_filter = ('is_default', 'is_combinable', 'allow_multiple', 'is_active')
    fields = ('verbose_name', 'name', 'is_default', 'is_combinable', 'allow_multiple')
    prepopulated_fields = {
        'name': ('verbose_name',)
    }
    change_readonly_fields = ('name',)
    inlines = [RateInline]


class ContractedPlanAdmin(AccountAdminMixin, admin.ModelAdmin):
    list_display = ('plan', 'account_link')
    list_filter = ('plan__name',)
    list_select_related = ('plan', 'account')


admin.site.register(Plan, PlanAdmin)
admin.site.register(ContractedPlan, ContractedPlanAdmin)

insertattr(Service, 'inlines', RateInline)
