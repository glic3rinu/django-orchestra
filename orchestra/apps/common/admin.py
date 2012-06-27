from django.contrib import admin
from django.contrib.contenttypes import generic
#from contacts.models import Contact, Contract

from django import forms
from signals import service_created, service_updated, service_deleted
#from common.utils.admin import filter_service_ct
#from models import Service
from ucp import settings as project_settings



from django.contrib.admin.filters import FieldListFilter, RelatedFieldListFilter
from django.utils.encoding import smart_unicode

#class FilterServiceContentType(RelatedFieldListFilter):

#    def __init__(self, field, request, params, model, model_admin, field_path):
#        super(FilterServiceContentType, self).__init__(
#            field, request, params, model, model_admin, field_path)
#        self.lookup_choices = self.get_choices(field,include_blank=False )

#    def get_choices(rat, self, include_blank=True, blank_choice=None):
#        """ Filter Service ContentType """
#        first_choice = include_blank and blank_choice or []
#        rel_model = self.rel.to
#        if hasattr(self.rel, 'get_related_field'):
#            lst = []
#            for x in rel_model._default_manager.complex_filter(self.rel.limit_choices_to):
#                if Service in x.model_class().__bases__:
#                    lst.append((getattr(x, self.rel.get_related_field().attname), smart_unicode(x)))
#        return first_choice + lst

#def _register_front(cls, test, factory):
#    """ FieldListFilter.register places the new FilterSpec at the back
#        of the list. This can be a problem, because the first 
#        matching FilterSpec is the one used. """

#    cls._field_list_filters.insert(0, (test, factory))

#TODO: apply this filter only to BaseAdmin class
#FieldListFilter.register_front = classmethod(_register_front)
#FieldListFilter.register_front(lambda f: 'content_type' is f.name, FilterServiceContentType)

#class BaseAdmin(admin.ModelAdmin): pass

    #TODO: do this without monkeypatching, Mixin!!
#    def get_form(self, request, obj=None, **kwargs):
#        def __init__(self, *args, **kwargs):
#            """ Filter content_type queryset with models that inherits from Service """ 
#            super(self.__class__, self).__init__(*args, **kwargs)
#            if self.fields.has_key('content_type'):
#                self.fields['content_type'].queryset = filter_service_ct(self.fields['content_type'].queryset)       
#    
#        form = super(BaseAdmin, self).get_form(request, obj=None, **kwargs)
#        form.__init__ = __init__
#        return form

#class ServiceAdmin(admin.ModelAdmin):

#    def log_change(self, request, object, message):
#        """ Send signal when save_model is fully executed """ 
#        service_updated.send(sender=object.__class__, request=request, instance=object)
#        super(ServiceAdmin, self).log_change(request, object, message)
#        
#    def log_addition(self, request, object):
#        """ Send signal when save_model is fully executed """ 
#        service_created.send(sender=object.__class__, request=request, instance=object)
#        super(ServiceAdmin, self).log_addition(request, object)

    # Please notice that service_deleted is trigged by django.models.post_save and it is placed on common.models


            
#class ServiceAdminInline(admin.options.InlineModelAdmin):
#    """ Create contrat for each inline form """ 
    #TODO: this is pure crap, refactor for christ sick
#    def get_formset(self, request, obj=None, **kwargs):
#        """ Pass request to formset and override save methods """ 
#        
#        def save_new(self, form, commit=True):
#            obj = self.super_save_new(form, commit=commit)
#            #TODO: Uses only when contacts app is installed or use ?contact_id=X
#            if not 'contact_id' in self.request.GET: 
#                contact = self.instance.contact
#                service_inserted.send(sender=ServiceAdmin, request=self.request, contact=contact, obj=obj)
#            else: service_inserted.send(sender=ServiceAdmin, request=self.request, obj=obj)
#            return obj

#        def save_existing(self, form, instance, commit=True):
#            _form = self.super_save_existing(form, instance, commit=commit)
#            service_updated.send(sender=ServiceAdmin, obj=instance)
#            return _form
#        

#        #TODO: how can it works if it's inherited from object ?
#        formset = super(ServiceAdminInline, self).get_formset(request, obj=None, **kwargs)
#        #FIXME: This not work with multiInheritance
#        formset.super_save_new = formset.save_new
#        formset.save_new = save_new
#        formset.super_save_existing = formset.save_existing
#        formset.save_existing = save_existing
#        formset.request = request
#        return formset
    

#class ServiceAdminTabularInline(ServiceAdminInline, admin.TabularInline):
#    pass


#class ServiceAdminStackedInline(ServiceAdminInline, admin.StackedInline):
#    pass


class AddOrChangeInlineFormMixin(admin.options.InlineModelAdmin):
    """ This mixin class provides support for use independent forms for change and add on admin inlines
        just define them as an atribute of the inline class, ie:
        
            add_form = AddSystemUserInlineForm
            change_form = ChangeSystemUserInlineForm
     """
    
    def get_formset(self, request, obj=None, **kwargs):
        """ Returns a BaseInlineFormSet class for use in admin add/change views.
            Adds support for distinct between add or change inline form 
        """
        # Determine if we need to use add_form or change_form
        field_name = self.model._meta.module_name
        try: 
            getattr(obj, field_name)
        except (self.model.DoesNotExist, AttributeError): 
            self.form = self.add_form
        else: 
            self.form = self.change_form
        
        return super(AddOrChangeInlineFormMixin, self).get_formset(request, obj=obj, **kwargs) 
        
#class PluginAdminTabularInline(admin.TabularInline):
            


#class ServiceAdminForm(forms.ModelForm):
#    # Moved to contacts.admin_contact_support
#    #TODO: delete
#    pass



         
#class PluginAdmin(admin.ModelAdmin):
#    
#    #TODO: sender = PluginAdmin?
#    def log_change(self, request, object, message):
#        """ Send signal when save_model is fully executed """ 
#        service_updated.send(sender=ServiceAdmin, instance=object.content_object)
#        super(PluginAdmin, self).log_change(request, object, message)
#        
#    def log_addition(self, request, object):
#        """ Send signal when save_model is fully executed """ 
#        service_updated.send(sender=ServiceAdmin, instance=object.content_object)
#        super(PluginAdmin, self).log_addition(request, object)
#                
#    def log_deletion(self, request, object, object_repr):
#        service_updated.send(sender=ServiceAdmin, instance=object.content_object)
#        super(PluginAdmin, self).log_deletion(request, object, object_repr)        



#from common.register import register,  _import
#from common.admin import ServiceAdmin
#from django.contrib import admin 



#class ServiceAdminRegister(object):
#    admins = []
#    model_map = {}
#    
#    def __init__(self):
#        for model in register.models:
#            # Load admin.py in case it's not in order to fill admin.sites._registry
#            _import("%s.admin" % model.__module__[:model.__module__.rfind('.')])
#            service_admin = admin.site._registry[model].__class__
##            if not ServiceAdmin in service_admin.__mro__:
##                if not admin.options.ModelAdmin == service_admin:
##                    name = "mixed_%s_with_%s" % (service_admin.__name__, ServiceAdmin.__name__)
##                    MixedAdmin = type(name, (service_admin, ServiceAdmin), {})
##                    admin.site.unregister(model)
##                    admin.site.register(model, MixedAdmin)                    
##                    self.admins.append(MixedAdmin)
#            service_admin.__bases__ = (ServiceAdmin,) + service_admin.__bases__
#            admin.site.unregister(model)
#            admin.site.register(model, service_admin)                                
#            self.admins.append(service_admin)
#            self.model_map[service_admin] = model
#            
#register = ServiceAdminRegister()



# Monkey-Patching models.deletion.collector in order to provide deletion on models
# with M2M field and delete_out_of_m2m attribute set to True

from django.db import models
from django.contrib.admin.util import NestedObjects
def m2m_collect(self, objs, source_attr=None, **kwargs):
    for obj in objs:
        if source_attr:
            related = getattr(obj, source_attr)
            if related.__class__.__name__ == 'ManyRelatedManager':
                related = related.all()[0]
            self.add_edge(related, obj)
        else:
            self.add_edge(None, obj)
    try:
        return super(NestedObjects, self).collect(objs, source_attr=source_attr, **kwargs)
    except models.ProtectedError, e:
        self.protected.update(e.protected_objects)

NestedObjects.collect = m2m_collect

