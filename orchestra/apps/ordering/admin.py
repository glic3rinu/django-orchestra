from common.utils.admin import UsedContentTypeFilter, get_modeladmin, content_object_link, DefaultFilterMixIn
from django.conf.urls.defaults import patterns, url, include
from django.contrib import messages, admin
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import get_model
from django.http import HttpResponseRedirect
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from forms import ServiceAccountingAdminForm
from models import Order, MetricStorage, Pack, ContractedPack, Tax, ServiceAccounting, Rate
import settings
from views import billing_options_view


contact_model = get_model(*settings.ORDERING_CONTACT_MODEL.split('.'))


class ContractPackAdmin(admin.ModelAdmin):
    actions = ['contract_pack', 'cancel_contract']

    def get_actions(self, request):
        actions = super(ContractPackAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def changelist_view(self, request, contact_id, extra_context=None):
        contact = contact_model._default_manager.get(pk=contact_id)
                
        def contracted(pack):
            """ Show link to invoice that has been sent """
            return True if ContractedPack.objects.active(pack=pack, contact=contact) else False
        contracted.short_description = _("Contracted")
        contracted.boolean = True

        def number(pack):
            """ Show link to invoice that has been sent """
            return ContractedPack.objects.active(pack=pack, contact=contact).count()
        contracted.short_description = _("Contracted")
        contracted.allow_tags = True    
    
        # list_display must be defined/overrided inside this closure kuz it depends on each contact
        self.list_display = ('name', contracted, number, 'allow_multiple', )
            
        context = {'title': _('Contract Pack for contact %s %s') % (contact.name, contact.surname),}
        context.update(extra_context or {}) 
        
        return super(ContractPackAdmin, self).changelist_view(request, extra_context=context)

    def get_contact(self, request): 
        contact_id = request.META['PATH_INFO'].split('/contract_pack/')[1].split('/')[0]
        return contact_model._default_manager.get(pk=contact_id)

    @transaction.commit_on_success
    def contract_pack(self, request, queryset):
        contact = self.get_contact(request)
        fail, success = [], []
        for pack in queryset:
            try: contract = ContractedPack.objects.create(pack=pack, contact=contact)
            except ValidationError: fail.append(pack.name)
            else: success.append(pack.name)
        if success: messages.add_message(request, messages.INFO, "Successful contracted for %s" % ",".join(success))
        if fail: messages.add_message(request, messages.ERROR, "Contraction aborted for %s" % ",".join(fail))
        return
        
    @transaction.commit_on_success
    def cancel_contract(self, request, queryset):
        contact = self.get_contact(request)
        fail, success = [], []
        for pack in queryset:
            try: contract = ContractedPack.objects.active(pack=pack, contact=contact)[0]
            except IndexError: fail.append(pack.name)
            else: 
                success.append(pack.name)
                contract.delete()
        if success: messages.add_message(request, messages.INFO, "Successful canceled for %s" % ",".join(success))
        if fail: messages.add_message(request, messages.WARNING, "No contract to cancel for %s" % ",".join(fail))
        return 
        
    def add_view(self, request, contact_id):
        return super(ContractPackAdmin, self).add_view(request)
    
    def change_view(self, request, object_id, contact_id):
        return super(ContractPackAdmin, self).change_view(request, object_id)
        
    def response_change(self, request, obj):
        # Redirect back to ContractedPack.change_list
        if not "_continue" in request.POST and not "_saveasnew" in request.POST and not "_addanother" in request.POST:
            msg = _('The Pack "%s" was changed successfully.') % force_unicode(obj)
            self.message_user(request, msg)
            if self.has_change_permission(request, None):
                post_url = reverse('admin:ordering_pack_changelist', current_app=self.admin_site.name)
                post_url += "contract_pack/%s/" % self.get_contact(request).pk
            else:
                post_url = reverse('admin:index', current_app=self.admin_site.name)
            return HttpResponseRedirect(post_url)
        return super(ContractPackAdmin, self).response_change(request, obj)
        
contact_modeladmin = get_modeladmin(contact_model)
if hasattr(contact_modeladmin, 'change_shorcut_links'):
    contact_modeladmin.change_shorcut_links.append(('"../../../ordering/pack/contract_pack/%s" % object_id', "addlink", _('Contract Pack')))

class PackAdmin(admin.ModelAdmin):

    list_display = ('name', 'allow_multiple', )
    list_filter = ('allow_multiple',)
    #contract_rel_url = '/contract_pack/'
    #TODO: What is the reverse url for this view?

    def get_urls(self):
        """Returns the additional urls used by the Contact admin."""
        urls = super(PackAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.module_name,
        select_urls = patterns("",
            url("^contract_pack/(?P<contact_id>\d+)/", include(ContractPackAdmin(Pack, admin_site).get_urls()), name="admin:ordering_contract_pack"),)
        return select_urls + urls 


class RateInline(admin.TabularInline):
    model = Rate
    fk_name = 'service'


class ServiceAccountingAdmin(admin.ModelAdmin):
    inlines = [RateInline,]
    form = ServiceAccountingAdminForm
    actions = ['fetch_service', 'disable_service', 'active_service']
    list_display = ('description', 'content_type', 'is_fee', 'pricing_period', 'billing_period', 'payment', 'tax')
    list_filter = (UsedContentTypeFilter, 'billing_period', 'is_fee',  )
    fieldsets = ((None,     {'fields': (('description',), 
                                        ('content_type',),
                                        ('expression'),)}),
                 ('Billing Period',{'fields': (('billing_period',),
                                                ('billing_point'),
                                                ('payment', 'on_prepay', 'discount'),)}),
                 ('Pricing Period',{'fields': (('pricing_period',),
                                                ('pricing_point',),
                                                ('pricing_effect',),)}),
                 ('Pricing',{'fields': (('pricing_with',),
                                        ('metric',),
                                        ('metric_get',),                                        
                                        ('metric_discount',),
                                        ('weight_with'),
                                        ('orders_with'),
                                        ('rating',),)}),
                 (None,     {'fields': (('tax'),
                                        ('is_fee'),
                                        )}), 
                )

    @transaction.commit_on_success
    def fetch_service(modeladmin, request, queryset):
        for service in queryset:
            service.fetch()
        messages.add_message(request, messages.INFO, _("All Selected services has been fetched"))
        return
    
    @transaction.commit_on_success
    def disable_service(modeladmin, request, queryset):
        for service in queryset:
            service.disable()
        messages.add_message(request, messages.INFO, _("All Selected services has been disabled"))
        return
    
    @transaction.commit_on_success
    def active_service(modeladmin, request, queryset):
        for service in queryset:
            service.activate()
        messages.add_message(request, messages.INFO, _("All Selected services has been activated"))
        return


class MetricStorageAdmin(admin.ModelAdmin):
    list_display = ('order', 'value', 'date')


class MetricStorageAdminInline(admin.TabularInline):
    model = MetricStorage    
    extra = 0
    can_delete = False
    max_num = 0
    readonly_fields = ('value', 'date',)


def cancel_date(self):
    return self.cancel_date if self.cancel_date else ''
cancel_date.short_description = _("Cancel date")


def billed_until(self):
    return self.billed_until if self.billed_until else ''
billed_until.short_description = _("Billed until")


def contact_link(self):
    app_label, model_name = settings.ORDERING_CONTACT_MODEL.split('.')
    url = reverse('admin:%s_%s_change' % (app_label, model_name.lower()), args=[self.contact.pk])
    return '<a href="%(url)s"><b>%(contact)s</b></a>' % {'url': url, 'contact': self.contact}
contact_link.short_description = _('Contact')
contact_link.allow_tags = True
contact_link.admin_order_field = 'contact'


def service_bold(self):
    return "<b>%s</b>" % self.service
#TODO: use decorators for all this shit
service_bold.short_description = _("Service")
service_bold.allow_tags = True
service_bold.admin_order_field = 'service'


class OrderAdmin(DefaultFilterMixIn):
    search_fields = ['service__description',]
    list_display = ('description', content_object_link, service_bold, contact_link, 'metric', 'register_date', cancel_date, billed_until, 'ignore', )
    date_hierarchy = 'register_date'
    list_filter = ('ignore', UsedContentTypeFilter)
    list_editable = ('ignore',)
    default_filter = 'ignore=0'
    inlines = [MetricStorageAdminInline,]
    actions = ['bill_orders', 'get_fake_bills', 'bill_orders_default_behaviour']

    @transaction.commit_on_success
    def bill_orders(modeladmin, request, queryset):
        return billing_options_view(modeladmin, request, queryset)

    @transaction.commit_on_success
    def bill_orders_default_behaviour(modeladmin, request, queryset):
        b_qset = queryset
        if settings.ORDERING_DEFAULT_DEPENDENCIES_EFFECT != settings.IGNORE_DEPENDENCIES:
            queryset_pks = list(queryset.values_list('pk', flat=True))
            dependencies = get_billing_dependencies(queryset, exclude=queryset_pks)
            if dependencies:
                if settings.ORDERING_DEFAULT_DEPENDENCIES_EFFECT == settings.BILL_DEPENDENCIES: 
                    dep_pks = [order.pkp for order in dependencies]
                    b_qset = Order.objects.filter(pk__in=queryset_pks.extend(dep_pks))
                dependencies = Order.objects.filter(pk__in=dep_pks)
        else: dependencies = []
        return confirm_bill_view(modeladmin, request, b_qset, 
                                 bill_point=datetime.now().strftime("%Y-%m-%d"), 
                                 fixed_point=settings.ORDERING_DEFAULT_FIXED_POINT, 
                                 force_next=settings.ORDERING_DEFAULT_FORCE_NEXT, 
                                 create_new_open=settings.ORDERING_DEFAULT_CREATE_NEW_OPEN, 
                                 dependencies=dependencies)
    
    def get_fake_bills(modeladmin, request, queryset): pass


admin.site.register(ServiceAccounting, ServiceAccountingAdmin)
admin.site.register(Pack, PackAdmin)
admin.site.register(Tax)
admin.site.register(Order, OrderAdmin)
admin.site.register(ContractedPack)
admin.site.register(MetricStorage)
