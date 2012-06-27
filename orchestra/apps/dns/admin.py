from django.contrib import admin
from models import Zone, Record, NameServer, Name
#from common.admin import ServiceAdmin, ServiceAdminTabularInline
#from reversion.admin import VersionAdmin
from django import forms
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
import settings
from django.utils.functional import curry
from common.forms import get_initial_form, get_initial_formset
from contacts.models import Contract, Contact
from django.db.models import Q
        
#TODO: recover Nameserver form rev 798

class RecordInline(admin.TabularInline):
    model = Record
    extra = 1
    form = get_initial_form(Record)
    formset = get_initial_formset(form)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(RecordInline, self).get_formset(request, obj, **kwargs)
        if not obj:
            initial = settings.DEFAULT_DOMAIN_REGISTERS
            formset.__init__ = curry(formset.__init__, initial=initial)
        return formset

#class SubdomainInline(ServiceAdminTabularInline):
#    model = Subdomain
#    fk_name = 'domain'
#    extra = 1 
#    form = get_initial_form(Domain)
#    formset = get_initial_formset(form)
#
#    def get_formset(self, request, obj=None, **kwargs):
#        formset = super(SubdomainInline, self).get_formset(request, obj, **kwargs)
#        if not obj:
#            initial = settings.DEFAULT_SUBDOMAINS
#            formset.__init__ = curry(formset.__init__, initial=initial)
#        return formset


def domain_link(self):
    return '<a href="http://%s">http://%s</a>' % (self, self)

domain_link.short_description = _("Domain link")
domain_link.allow_tags = True

class ZoneAdmin(admin.ModelAdmin):
    list_display = ['origin', domain_link, ]

    fieldsets = ((None,     {'fields': (('origin',), 
                                        ('primary_ns', 'hostmaster_email'),
                                        )}),
        ('Optional Fields', {'classes': ('collapse',),
                             'fields': (('serial',),
                                        ('slave_refresh',),
                                        ('slave_retry',),
                                        ('slave_expiration',),
                                        ('min_caching_time'),)}),)
    inlines = [RecordInline,]
    
#TODO: create a factory class for initial tabular inline forms. keep it DRY
class NameServerInline(admin.TabularInline):
    model = NameServer
    extra = 1
    form = get_initial_form(NameServer)
    formset = get_initial_formset(form)
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super(NameServerInline, self).get_formset(request, obj, **kwargs)
        if not obj:
            initial = settings.DEFAULT_NAME_SERVERS
            formset.__init__ = curry(formset.__init__, initial=initial)
        return formset    


def domain_link(self):
    return '<a href="http://%s">http://%s</a>' % (self, self)

domain_link.short_description = _("Domain link")
domain_link.allow_tags = True

def zone_link(self):

    zone = self.get_zone() 
    if zone is None:
        path = reverse('admin:dns_zone_add')
        #TODO: contact link must be implemented on contacts app
        path += '?contact_id=%s&origin=%s.%s' % (self.contact.pk, self.name, self.extension)
        return '<a href="%s">Add Zone</a>' % (path)
    else:
        path = reverse('admin:dns_zone_change', args=(zone.pk,))
        return '<a href="%s">%s</a>' % (path, zone.origin)

zone_link.short_description = _("Zone link")
zone_link.allow_tags = True

def domain(self):
    return self
domain.short_description = _("Domain")
domain.admin_order_field = 'name'

class NameAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NameAdminForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            # Add form
            contact = Contact.objects.get(pk=kwargs['initial']['contact_id'])
            self.fields['administrative_contact'].initial = contact.administrative_contact.pk
            self.fields['technical_contact'].initial = contact.technical_contact.pk
            self.fields['billing_contact'].initial = contact.billing_contact.pk                
            self.contact = contact
            
        else:
            try: self.contact = self.instance.contact
            except Contract.DoesNotExist: return

        qset = Q(Q(contact__pk=self.contact.pk)|
            Q(billingcontact__contact__pk=self.contact.pk)|
            Q(administrativecontact__contact__pk=self.contact.pk)|
            Q(technicalcontact__contact__pk=self.contact.pk))

        self.fields['administrative_contact'].queryset = self.fields['administrative_contact'].queryset.filter(qset)
        self.fields['technical_contact'].queryset = self.fields['technical_contact'].queryset.filter(qset)
        self.fields['billing_contact'].queryset = self.fields['billing_contact'].queryset.filter(qset)

class NameAdmin(admin.ModelAdmin):
    list_display = [domain, 'extension', zone_link, 'register_provider', ]
    list_filter = ['extension', 'register_provider']
#    list_editable = ('mail',)
    inlines = [NameServerInline,]
    form = NameAdminForm
    fieldsets = ((None, {'fields': (('name', 'extension',), 
                                    ('register_provider',),
                                    ('administrative_contact',),
                                    ('technical_contact',),
                                    ('billing_contact',),)}),)

#    filter_fields_by_contact = ('contact',)

admin.site.register(Zone, ZoneAdmin)
admin.site.register(Name, NameAdmin)


from common.signals import service_created, service_updated
from django.dispatch import receiver

@receiver(service_created, sender=Zone, dispatch_uid="name.create_names")
@receiver(service_updated, sender=Zone, dispatch_uid="name.update_names")
def create_names(sender, **kwargs):
    # 1. Deletes on Zone doesn't affect names
    # 2. Creates and Updates on Zone only produces creates on Name
    zone = kwargs['instance']
    request = kwargs['request']
    for domain_name in zone.get_names():
        name, extension = Name.split(domain_name)
        try: Name.objects.get(name=name, extension=extension)
        except Name.DoesNotExist:
            new_name = Name(name=name, extension=extension, register_provider='')
            new_name.save()
            service_created.send(sender=Name, request=request, instance=new_name, origin=zone)
