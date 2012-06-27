from common.utils.python import _import
from django.contrib.contenttypes import generic
from django.db import models
import settings


class ContractedRegister(object):
    models = []
    model_extensions = []
    generic_extensions = []
    
    def __init__(self):
        for module in settings.CONTRACTED_MODELS:
            try: model = _import(module)
            except ImportError: continue 
            #model.__bases__ = (Service,)
            self.models.append(model)
            # FK
            self.model_extensions += model._meta.get_all_related_objects()
            # M2M and GFK
            #TODO: avoid repetitions on model_extentions
            for m2m in model._meta.many_to_many:
                if isinstance(m2m, generic.GenericRelation):
                    self.generic_extensions.append(m2m.related)

register = ContractedRegister()


@property
def contact(self):
    return self.contract.contact   


@property
def contract(self):
    return self.related_contract.get()


#from common.register import register
for model in register.models:
    #TODO: create a custom GenericRelation representing OnToOneGenericRelations. 
    # Otherwise the admin order field will behave a bit strange
    generic.GenericRelation('contacts.Contract', related_name="%(app_label)s_%(class)s_related").contribute_to_class(model, 'related_contract')
    model.contact = contact
    model.contract = contract


# Provides contact and contract relation to "service extentions"
for related in register.model_extensions:
    # We are using the default arg trick in order to stick the current (declaration time)
    # related.field.name to the function, otherwise it will use the value on runtime 
    @property
    def contact(self, name=related.field.name): 
        return getattr(self, name).contact 
    
    if not hasattr(related.model, 'contact'):
        related.model.contact = contact

    @property
    def contract(self, name=related.field.name): 
        return getattr(self, name).contract 

    if not hasattr(related.model, 'contract'):
        related.model.contract = contract


# Generic relations: seems to work inverse of FKs
#TODO: sure there is a way to combine with model_extensions (DRY)
for related in register.generic_extensions:
    # related.field.name to the function, otherwise it will use the value on runtime 
    @property
    def contact(self): 
        return getattr(self, 'content_object').contact 
    
    if not hasattr(related.parent_model, 'contact'):
        related.parent_model.contact = contact

    @property
    def contract(self): 
        return getattr(self, 'content_object').contract 

    if not hasattr(related.parent_model, 'contract'):
        related.parent_model.contract = contract    
