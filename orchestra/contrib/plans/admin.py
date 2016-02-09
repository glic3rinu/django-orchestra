from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import insertattr, admin_link
from orchestra.contrib.accounts.actions import list_accounts
from orchestra.contrib.accounts.admin import AccountAdminMixin
from orchestra.contrib.services.models import Service

from .models import Plan, ContractedPlan, Rate


class RateInline(admin.TabularInline):
    model = Rate
    ordering = ('service', 'plan', 'quantity')


class PlanAdmin(ExtendedModelAdmin):
    list_display = (
        'name', 'is_default', 'is_combinable', 'allow_multiple', 'is_active', 'num_contracts',
    )
    list_filter = ('is_default', 'is_combinable', 'allow_multiple', 'is_active')
    fields = ('verbose_name', 'name', 'is_default', 'is_combinable', 'allow_multiple')
    prepopulated_fields = {
        'name': ('verbose_name',)
    }
    change_readonly_fields = ('name',)
    inlines = [RateInline]
    
    def num_contracts(self, plan):
        num = plan.contracts__count
        url = reverse('admin:plans_contractedplan_changelist')
        url += '?plan__name={}'.format(plan.name)
        return '<a href="{0}">{1}</a>'.format(url, num)
    num_contracts.short_description = _("Contracts")
    num_contracts.admin_order_field = 'contracts__count'
    num_contracts.allow_tags = True
    
    def get_queryset(self, request):
        qs = super(PlanAdmin, self).get_queryset(request)
        return qs.annotate(models.Count('contracts', distinct=True))


class ContractedPlanAdmin(AccountAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'plan_link', 'account_link')
    list_filter = ('plan__name',)
    list_select_related = ('plan', 'account')
    search_fields = ('account__username', 'plan__name', 'id')
    actions = (list_accounts,)
    
    plan_link = admin_link('plan')


admin.site.register(Plan, PlanAdmin)
admin.site.register(ContractedPlan, ContractedPlanAdmin)

insertattr(Service, 'inlines', RateInline)
