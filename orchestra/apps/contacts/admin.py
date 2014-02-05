from django.conf.urls import patterns, url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import wrap_admin_view, get_modeladmin
from orchestra.models.utils import get_model

from . import settings
from .models import Contact, Contract


admin.site.register(Contact)
admin.site.register(Contract)


class ContactListAdmin(admin.ModelAdmin):
    """ Contact list to allow contact selection when creating new services """
    fields = ('short_name', 'full_name')
    list_display = ('contact_link', 'full_name')
    actions = None
    search_fields = ['short_name', 'full_name']
    ordering = ('full_name',)
    
    def contact_link(self, instance):
        context = {
            'url': '../?contact_id=' + str(instance.pk),
            'contact_name': instance.full_name
        }
        return '<a href="%(url)s">%(contact_name)s</a>' % context
    contact_link.short_description = _("contact")
    contact_link.allow_tags = True
    
    def changelist_view(self, request, extra_context=None):
        opts = self.model._meta
        original_app_label = request.META['PATH_INFO'].split('/')[-5]
        original_model = request.META['PATH_INFO'].split('/')[-4]
        context = {
            'title': _("Select contact for adding a new %s") % (original_model),
            'original_app_label': original_app_label,
            'original_model': original_model,
        }
        context.update(extra_context or {})
        return super(ContactListAdmin, self).changelist_view(request,
                extra_context=context)


class ContractAdminMixin(object):
    def contact_link(self, instance):
        contact = instance.contact
        url = reverse('admin:contacts_contact_change', args=(contact.pk,))
        return '<a href="%s">%s</a>' % (url, contact.full_name)
    contact_link.short_description = _("contact")
    contact_link.allow_tags = True
    contact_link.admin_order_field = 'related_contract__contact__full_name'
    
    def get_list_display(self, request):
        list_display = super(ContractAdminMixin, self).get_list_display(request)
        return list_display + ('contact_link',)
    
    def get_urls(self):
        """ Hooks select contact url """
        urls = super(ContractAdminMixin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.module_name
        contact_list = ContactListAdmin(Contact, admin_site).changelist_view
        select_urls = patterns("",
            url("/select-contact/$",
                wrap_admin_view(self, contact_list),
                name='%s_%s_select_contact' % info),
        )
        return select_urls + urls 
    
    def add_view(self, request, form_url='', extra_context=None):
        """ Redirects to select contact view if required """
        if request.user.is_superuser:
            if 'contact_id' in request.GET or Contact.objects.count() == 1:
                kwargs = {}
                if 'contact_id' in request.GET:
                    kwargs = dict(pk=request.GET['contact_id'])
                contact = Contact.objects.get(**kwargs)
                opts = self.model._meta
                context = {
                    'contact_id': contact.pk,
                    'title': _("Add %s for %s") % (opts.verbose_name, contact.full_name)
                }
                context.update(extra_context or {})
                return super(ContractAdminMixin, self).add_view(request,
                        form_url=form_url, extra_context=context)
        return HttpResponseRedirect('./select-contact/')
    
    def log_addition(self, request, object):
        """ Create a contract when a new object is created """
        if not request.user.is_superuser:
            contact = request.user.contact
        elif 'contact_id' in request.GET:
            contact = Contact.objects.get(pk=request.GET['contact_id'])
        else:
            contact = Contact.objects.get()
        Contract.objects.create(contact=contact, content_object=object)
        super(ContractAdminMixin, self).log_addition(request, object)


for model_label in settings.CONTACTS_CONTRACT_MODELS:
    # Hook ContractAdminMixin to CONTACTS_CONTRACT_MODELS model admins
    model = get_model(model_label)
    modeladmin = get_modeladmin(model)
    if ContractAdminMixin not in type(modeladmin).__mro__:
        bases = (ContractAdminMixin,) + type(modeladmin).__bases__
        if admin.ModelAdmin not in bases:
            raise TypeError('%s admin needs a declared admin class' % model_label)
        type(modeladmin).__bases__ = bases
