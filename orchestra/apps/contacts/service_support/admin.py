from common.utils.python import mixin,  _import
from contacts.models import Contact, Contract
from contacts.widgets import ContactRelatedFieldWidgetWrapper        
from django import forms 
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from views import select_contact_view
from models import register


""" This have their own app in order to avoid circular imports between common.admin and contacts.admin """


class ContactAdminFormMixin(forms.ModelForm):
    filter_fields_by_contact = []
    filter_unique_fields = []
    
    def __init__(self, *args, **kwargs):
        """ limite FK form queryset to contracted stuff """ 
        super(ContactAdminFormMixin, self).__init__(*args, **kwargs)
        if 'instance' in kwargs: 
            self.contact_id = self.instance.contact.pk
        elif 'contact_id' in self.initial:
            self.contact_id = self.initial['contact_id']
        # Last try check if 'contact_id' has been injected by get_formset
        elif not hasattr(self, 'contact_id'): 
            # __init__ is called when rendering form and when save form. 
            # There is a problem: when save new form insance and initial values doesn't exist :(
            # Fortunatly at this point there is no need to filter field.queryset so we return from method        
            return
        #TODO: make exceptions in objects_pk in order to allow shared instances.
        # filter_fields_by_contact contains field names that you whant to filter by contracted for the same contact
        # If there is an intermediary model like domain > name > domain you can use field__field_rel1__field_rel2 to reach the final model 
        # Example: filter_fields = ['user', 'domain__domain', 'domain__subdomain', ]
        # exclude_objects = {'domain': (1,2,3,4),}
        s_filter_fields = list(self.filter_fields_by_contact)
        result = {}
        for field in s_filter_fields:
            names = field.split('__')
            models = []
            ant = self._meta.model
            for name in names:
                current = ant.__dict__[name].field.rel.to
                models.append(current)
                ant = current

            ct = ContentType.objects.get_for_model(models[-1])
            object_pks = Contract.objects.filter_active_by_contact(self.contact_id).filter(content_type=ct).values_list('object_id', flat=True)

            if len(names) > 1:
                # Contracted model is a related one
                query = ""
                for name in names[1:]:
                    query += "%s__" % name
                query += "pk__in"
                object_pks = models[0].objects.filter(**{query: object_pks}).values_list('pk', flat=True)

            field_name = names[0]
            if field_name in result.keys():
                result[field_name].union(set(object_pks))
            else: 
                result[field_name] = set(object_pks)
        for field in result.keys():    
            self.fields[field].queryset = self.fields[field].queryset.filter(pk__in=result[field])
        # NOTE: Despite of user is defined with unique=True in model def. Add/change form seems to ignore it. 
        # filter_unique_fields = ('user', )field
        for field in self.filter_unique_fields: 
            instance_pks = set()
            if 'instance' in kwargs: 
                # FK
                try: instance_pks = set((getattr(self.instance, field).pk,))
                except AttributeError: 
                    # M2M
                    field_accessor = getattr(self.instance, field)
                    instance_pks = set(field_accessor.all().values_list('pk', flat=True))

            model = self._meta.model
            field_model = model.__dict__[field].field.rel.to
            # domains=None: exclude emtpy vhosts (not necessary but for improve resilience)
            objects_pk = model.objects.exclude(domains=None).values_list('%s__pk' % field, flat=True)
            self.fields[field].queryset = self.fields[field].queryset.exclude(pk__in=(set(objects_pk)-instance_pks))
            
def service_admin_form_mixin(model_admin):
    form_class = model_admin.form
    model = model_admin.model
    contact_fields = model_admin.filter_fields_by_contact
    unique_fields = model_admin.filter_unique_fields
    
    Meta = type("Meta", (), {"model": model})
    ServiceAdminForm = type("ServiceAdminForm", (ContactAdminFormMixin, ), {"filter_fields_by_contact": contact_fields, 
                                                                            "filter_unique_fields": unique_fields,
                                                                            "Meta": Meta})    
    # KISS ;) this logic is for avoiding some circular MRO problems
    if form_class is forms.ModelForm:
        return ServiceAdminForm
    else:
        mixin(form_class, ServiceAdminForm, first=True)
        return form_class


from models import register
def provide_contact_addlink(base_admin, formfield, db_field, request, inline):
    """ Add contact_id?=x to formfield addlink """    
    if formfield and isinstance(formfield.widget.__class__, admin.widgets.RelatedFieldWidgetWrapper):
        if db_field.rel.to in register.models:
            related_modeladmin = base_admin.admin_site._registry.get(db_field.rel.to)
            can_add_related = bool(related_modeladmin and
                        related_modeladmin.has_add_permission(request))

            if 'contact_id' in request.GET:
                contact_id = request.GET['contact_id']
            else: 
                #TODO: Must be another way to get the object.
                object_id = request.META['PATH_INFO'].split('/')[-2]
                #THIS IS THE ONLY DIFFERENT LINE
                if inline: 
                    contact_id = base_admin.parent_model.objects.get(pk=object_id).contract.contact.pk
                else:
                    contact_id = base_admin.get_object(request, object_id).contract.contact.pk                        
                
            formfield.widget = ContactRelatedFieldWidgetWrapper(formfield.widget,
                db_field.rel, base_admin.admin_site, can_add_related=can_add_related, contact_id=contact_id)

    return formfield

def contact_link(self):
    contact = self.contact
    url = reverse('admin:contacts_contact_change', args=(contact.pk,))
    return '<a href="%(url)s">%(contact_name)s</a>' % {'url': url , 'contact_name': contact.fullname  }
    
contact_link.short_description = _("Contact Link")
contact_link.allow_tags = True
#TODO: we need to find a way to filter this query with distinct('related_contract__contact__name')
contact_link.admin_order_field = 'related_contract__contact__name'

class ContactSupportAdminMixin(admin.ModelAdmin):
    change_form_template = "service/change_form.html"
    contract_rel_url = '/add/?contact_id='
    
    filter_fields_by_contact = []
    filter_unique_fields = []
    
    def __init__(self, *args, **kwargs):
        super(ContactSupportAdminMixin, self).__init__(*args, **kwargs)
        self.list_display += (contact_link, )
        self.form = service_admin_form_mixin(self)
        #FIXME: this can't be applied without breaking the user add view
#        if hasattr(self, 'add_form'): 
#            self.add_form = service_admin_form_mixin(self)
#        if hasattr(self, 'change_form'): 
#            self.change_form = service_admin_form_mixin(self)
            
    def get_urls(self):
        """Returns the additional urls used by the Contact admin."""
        urls = super(ContactSupportAdminMixin, self).get_urls()
        #urls = self.super_get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.module_name,
        select_urls = patterns("",
            url("/select_contact/$", admin_site.admin_view(select_contact_view), {'model_admin': self}, name='%s_%s_select_contact' % info),)
        return select_urls + urls 

    def add_view(self, request, form_url='', extra_context=None):
        """ Override add view title """
        if 'contact_id' in request.GET:
            contact_id = request.GET['contact_id']
            contact = Contact.objects.get(pk=request.GET['contact_id'])
            opts = self.model._meta
            context = { 'contact_id': request.GET['contact_id'],
                        'content_title': _('Add %s for contact %s') % (opts.verbose_name, contact.fullname)}
            context.update(extra_context or {})        
            return super(ContactSupportAdminMixin, self).add_view(request, form_url='', extra_context=context)
        elif self.model is Contact: 
            return super(ContactSupportAdminMixin, self).add_view(request, form_url='', extra_context=extra_context)
        else: return HttpResponseRedirect("./select_contact/")


    def change_view(self, request, object_id, extra_context=None):
        """ Show contact name on form title. """
        obj = self.get_object(request, object_id)
        opts = self.model._meta
        contract = obj.contract
        contract.contact
        context = {
            'content_title': mark_safe(u'Change %s of contact %s' % (opts.verbose_name, contact_link(contract))),
            'contract_link': reverse('admin:contacts_contract_change', args=(contract.pk,))}
        context.update(extra_context or {})
        return super(ContactSupportAdminMixin, self).change_view(request, object_id, extra_context=context)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Add contact_id?=x to addlink """
        formfield = super(ContactSupportAdminMixin, self).formfield_for_dbfield(db_field, **kwargs)
        return provide_contact_addlink(self, formfield, db_field, kwargs.pop("request", None), inline=False)
        
    def get_inline_instances(self, *args, **kwargs):
        """ Provide inline contact support """
        for inline in self.inlines:
            if not ContactSupportInlineMixin in inline.__mro__:
                #FIXME: this is a hak kuz if we mixin this class with those inlines who doesn't have ""related objects filter_unique_form_fields""
                # to filter it generates some unknown exponential performance regression. mfw O_o
                if hasattr(inline, 'filter_fields_by_contact') or hasattr(inline, 'filter_unique_fields'):
                    mixin(inline, ContactSupportInlineMixin, last=True)
        return super(ContactSupportAdminMixin, self).get_inline_instances(*args, **kwargs)

    def log_addition(self, request, object):
        """ Send signal when save_model is fully executed """ 
        contact_id = request.GET['contact_id']
        contact = Contact.objects.get(pk=request.GET['contact_id'])        
        Contract.create(contact=contact, obj=object)
        super(ContactSupportAdminMixin, self).log_addition(request, object)

class ContactSupportInlineMixin(admin.options.InlineModelAdmin):
    filter_fields_by_contact = []
    filter_unique_fields = []
       
    def __init__(self, *args, **kwargs):
        super(ContactSupportInlineMixin, self).__init__(*args, **kwargs)
        self.form = service_admin_form_mixin(self)
        # Make it compatible with add_form/change_form support
        if hasattr(self, 'add_form'): 
            self.add_form = service_admin_form_mixin(self)
        if hasattr(self, 'change_form'): 
            self.change_form = service_admin_form_mixin(self)
                                                             
    def get_formset(self, request, obj=None, **kwargs):
        """ Provides contact_id for future usage on add/change form contact filtering """
        if 'contact_id' in request.GET: 
            self.form.contact_id = request.GET['contact_id']
        else:
            self.form.contact_id = obj.contact.pk
        return super(ContactSupportInlineMixin, self).get_formset(request, obj=obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Add contact_id?=x to addlink """
        formfield = super(ContactSupportInlineMixin, self).formfield_for_dbfield(db_field, **kwargs)
        return provide_contact_addlink(self, formfield, db_field, kwargs.pop("request", None), inline=True)


class ContactAdminRegister(object):
    admins = []
    model_map = {}
    
    def __init__(self):
        for model in register.models:
            # Load admin.py in case it's not in order to fill admin.sites._registry
            _import("%s.admin" % model.__module__[:model.__module__.rfind('.')])
            model_admin = admin.site._registry[model].__class__
            self.admins.append(model_admin)
            self.model_map[model_admin] = model

register = ContactAdminRegister()


for model_admin in register.admins:
    model = register.model_map[model_admin]
    admin.site.unregister(model)
    mixin(model_admin, ContactSupportAdminMixin, first=True)
    admin.site.register(model, model_admin)          

