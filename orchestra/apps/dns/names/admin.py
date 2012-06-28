from common.forms import get_initial_form, get_initial_formset
from contacts.models import Contract, Contact
from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.dispatch import receiver
from django.utils.functional import curry
from django.utils.translation import ugettext as _
from models import NameServer, Name
import settings


#TODO: create a factory class for initial tabular inline forms. keep it DRY
class NameServerInline(admin.TabularInline):
    model = NameServer
    extra = 1
    form = get_initial_form(NameServer)
    formset = get_initial_formset(form)
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super(NameServerInline, self).get_formset(request, obj, **kwargs)
        if not obj:
            initial = settings.DNS_DEFAULT_NAME_SERVERS
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
            self.fields['administrative_contact'].initial = contact.administrative.pk
            self.fields['technical_contact'].initial = contact.technical.pk
            self.fields['billing_contact'].initial = contact.billing.pk
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
    inlines = [NameServerInline,]
    form = NameAdminForm
    fieldsets = ((None, {'fields': (('name', 'extension',), 
                                    ('register_provider',),
                                    ('administrative_contact',),
                                    ('technical_contact',),
                                    ('billing_contact',),)}),)



admin.site.register(Name, NameAdmin)



