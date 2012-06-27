from common.utils.admin import UsedContentTypeFilter, content_object_link, get_modeladmin
from contacts.actions import cancel_contract, unsubscribe
from contacts.models import Contact, BaseContact, BillingContact, AdministrativeContact, TechnicalContact, Contract, Email, Phone, contract_updated
from contacts.service_support.models import register
from datetime import datetime
from django import template
from django.conf.urls.defaults import patterns, url
from django.contrib import admin, messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.encoding import force_unicode
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from forms import MailForm


class BillingContactInline(admin.StackedInline):
    model = BillingContact
    fk_name = 'contact'
    max_num = 1


class TechnicalContactInline(admin.StackedInline):
    model = TechnicalContact
    fk_name = 'contact'
    max_num = 1


class AdministrativeContactInline(admin.StackedInline):
    model = AdministrativeContact
    fk_name = 'contact'
    max_num = 1    


def contact_link(self):
    url = reverse('admin:contacts_contact_change', args=[self.contact.pk])
    return '<a href="%(url)s"><b>%(contact)s</b></a>' % {'url': url, 'contact': self.contact}
contact_link.short_description = _('Contact')
contact_link.allow_tags = True
contact_link.admin_order_field = 'contact'


def display_contract(self):
    return self
display_contract.short_description = _("Contract")
display_contract.admin_order_field = 'content_type'


def cancel_date(self):
    return self.cancel_date if self.cancel_date else ''
cancel_date.short_description = _("Cancel date")
cancel_date.admin_order_field = 'cancel_date'


def active(self):

    return not self.cancel_date or self.cancel_date > datetime.now()
active.short_description = _("Active")
active.boolean = True
active.admin_order_field = 'cancel_date'



class ContractAdmin(admin.ModelAdmin): 
    date_hierarchy = 'register_date'    
    search_fields = ['contact__name', 'description',]
    list_display = (display_contract, contact_link, 'content_type', content_object_link, 'description', 'register_date', cancel_date, active)    
    actions = [cancel_contract, ]
    list_filter = [UsedContentTypeFilter, 'cancel_date']


class EmailInline(admin.TabularInline):
    model = Email
    extra = 1


class PhoneInline(admin.TabularInline):
    model = Phone
    extra = 1


def contract_filter(self):
    url = reverse('admin:contacts_contract_changelist')
    return '<a href="%s?contact=%s">Contracts</a>' % (url, self.pk)
contract_filter.short_description = _("Contracts")
contract_filter.allow_tags = True


def zipcode(self):
    return self.zipcode if self.zipcode else ''
zipcode.short_description = _("Zipcode")
zipcode.admin_order_field = 'zipcode'


def fax(self):
    return self.fax if self.fax else ''
fax.short_description = _("Fax")
fax.admin_order_field = 'cancel_date'


class ContactAdmin(admin.ModelAdmin):
    date_hierarchy = 'register_date'    
    fieldsets = ((None,     {'fields': (('name', 'surname', 'second_surname'), 
                                        ('national_id', 'type'), ('language'),)}),
        ('Optional Fields', {'classes': ('collapse',),
                             'fields': (('address', 'city','zipcode','province','country'),
                                        ('fax'),'comments',)}),)
    inlines = [EmailInline, PhoneInline, BillingContactInline, TechnicalContactInline, AdministrativeContactInline]
    # TODO: howto use this with a property    
    # date_hierarchy = 'subscribe'
    list_display = ('name', 'surname', 'type', 'email', 'phone', fax, 'national_id', 'address', 'city', zipcode,'register_date', contract_filter)
    list_display_links = ('name', 'surname',)
    list_filter = ('is_staff', 'type')
    search_fields = ['name', 'surname', 'second_surname',]
    actions = ['bulk_service_contraction', 'send_bulk_mail', 'contract_service', unsubscribe]
    change_form_template = "admin/contacts/contact/change_form.html"
    contract_service_template = "admin/contacts/contact/contract_service.html"
    #TODO: add a insert_link method (packs)
    change_shorcut_links = [("reverse('admin:contacts_contact_contract_service', args=(object_id,))", "addlink", _('Contract Service')), ("reverse('admin:contacts_contract_changelist')+'?contact=%s' % (object_id)", "historylink", _('Contracted Services'))]

    class Media:
        js = ['js/collapsed_stacked_inlines.js',]

    def get_actions(self, request):
        actions = super(ContactAdmin, self).get_actions(request)
        #TODO: only for develope propose        
        #del actions['delete_selected']
        return actions

    def get_urls(self):
        """Returns the additional urls used by the Contact admin."""
        urls = super(ContactAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.module_name,
        contact_urls = patterns("",
            url("^contract_service/(?P<contact_id>\d+)/$", admin_site.admin_view(self.contract_service_view), name='%s_%s_contract_service' % info),)
        return contact_urls + urls 

    def change_view(self, request, object_id, extra_context=None):
        """ Add custom links on object-tools-items block """
        links = []
        models = register.models
        for link in self.change_shorcut_links:
            links.append((eval(link[0]), link[1], link[2]))        

        context = { 'shortcut_links': links }
        context.update(extra_context or {})
        return super(ContactAdmin, self).change_view(request, object_id, extra_context=context)

    def contract_service_view(self, request, contact_id, extra_context=None):
        """List all available services with links to a add_form based on contact_id"""
        contact = Contact.objects.get(pk=contact_id)
        model = self.model
        opts = model._meta
        models = set(register.models) - set([Contact,])
        
        services = [{'app':model_._meta.app_label, 
                     'model':model_._meta.module_name, 
                     'verbose_model':model_._meta.verbose_name, 
                     'rel_url': get_modeladmin(model_).contract_rel_url,} for model_ in models]

        context = {"opts": opts,
                   "app_label": opts.app_label,
                   "module_name": capfirst(opts.verbose_name),
                   "title": _("Contract service for contact %(name)s") % {"name": force_unicode(contact.fullname)},
                   "changelist_url": reverse("admin:%s_%s_changelist" % (opts.app_label, opts.module_name)),
                   "services": services,
                   "contact_id": contact_id,}
                   
        context.update(extra_context or {})
        #FIXME: I don't know why but the template regroup tag doesn't werk very well with services var
        return render_to_response(self.contract_service_template, context, template.RequestContext(request))
        
    def bulk_service_contraction(modeladmin, request, queryset):
        """ for packs and extra stuff """ 
        pass
        
    def send_bulk_mail(modeladmin, request, queryset):
        opts = modeladmin.model._meta
        app_label = opts.app_label
        
        if request.POST.get('post'):
            form = MailForm(request.POST)
            #TODO: display the validation errors
            if form.is_valid():
                mail_from = form.cleaned_data['mail_from']
                subject = form.cleaned_data['subject']
                body = form.cleaned_data['body']
                messages.add_message(request, messages.INFO, _("Message has beben delivered to mail server"))
                return
                
        form = MailForm()

        context = {
            "title": 'Send Bulk Mail',
            "form": form,
            "opts": opts,
            "app_label": app_label,
            "queryset": queryset,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
            'action_name': 'send_bulk_mail',
        }
        return render_to_response("contacts/schedule.html", context, 
                                  context_instance=template.RequestContext(request))
                  
    def contract_service(modeladmin, request, queryset):
        if len(queryset) > 1:
            messages.add_message(request, messages.ERROR, _("select a single object please"))
            return HttpResponseRedirect("./")
        else:
            selected = request.POST.get(admin.ACTION_CHECKBOX_NAME)
            return HttpResponseRedirect("./contract_service/"+"".join(selected))
        make_published.short_description = "Contract new service"

    def add_view(self, request, form_url='', extra_context=None):
        return super(ContactAdmin, self).add_view(request, form_url=form_url,
                    extra_context=extra_context)


admin.site.register(BaseContact)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Contract, ContractAdmin)


from django.conf import settings as django_settings
