from django.contrib.contenttypes import generic
from django.db import models
from django.db.models.signals import pre_delete
from django.db.models.deletion import Collector, CASCADE
from django.dispatch import receiver, Signal
from signals import service_deleted, collect_related_objects_to_delete
from utils.models import VirtualField, has_changed


has_been_enabled = Signal(providing_args=["obj", "message"])
has_been_disabled = Signal(providing_args=["obj", "message"])


@receiver(pre_delete, dispatch_uid="common.send_service_deleted")    
def send_service_deleted(sender, **kwargs):
    # NOTE: if we want to access to obj.related objects we must use pre_delete signal
    # If we want to execute the script when all related objects are gone: post_delete
    instance = kwargs['instance']
    service_deleted.send(sender=instance.__class__, instance=instance)


# Monkey-Patching models.deletion.collector in order to provide deletion on models
# with with M2M field and delete_out_of_m2m attribute set to True
# Also we avoid delete on cascade for GFK: TODO: make exceptions for resources 
Collector.org_collect = Collector.collect

def m2m_collect(self, objs, source=None, nullable=False, collect_related=True,
    source_attr=None, reverse_dependency=False, all_dependencies=False):

    """ if all_dependencies: return ALL m2m related objects of those with 
        delete_out_of_m2m, even if they are not rouning out of deletions
    
    """

    ## START COPYPASTA FROM DJANGO.DB.MODELS.DELETION.COLLECTOR.COLLECT
    new_objs = self.add(objs, source, nullable,
                        reverse_dependency=reverse_dependency)
    if not new_objs:
        return

    model = new_objs[0].__class__

    # Recursively collect parent models, but not their related objects.
    # These will be found by meta.get_all_related_objects()
    for parent_model, ptr in model._meta.parents.iteritems():
        if ptr:
            parent_objs = [getattr(obj, ptr.name) for obj in new_objs]
            self.collect(parent_objs, source=model,
                         source_attr=ptr.rel.related_name,
                         collect_related=False,
                         reverse_dependency=True)

    if collect_related:
        for related in model._meta.get_all_related_objects(
                include_hidden=True, include_proxy_eq=True):
            field = related.field
            if related.model._meta.auto_created:
                self.add_batch(related.model, field, new_objs)
            else:
                sub_objs = self.related_objects(related, new_objs)
                if not sub_objs:
                    continue
                field.rel.on_delete(self, field, sub_objs, self.using)
            
        # TODO This entire block is only needed as a special case to
        # support cascade-deletes for GenericRelation. It should be
        # removed/fixed when the ORM gains a proper abstraction for virtual
        # or composite fields, and GFKs are reworked to fit into that.
        for relation in model._meta.many_to_many:
    ## END COPYPASTA   
            # Avoid delete contracts
            #TODO: make it reusable !! 
            #      keep_on_delete atrribute on related_contract generic relation or something else?
            if relation.name != 'related_contract':
            #if not Service.is_service(model):
                if not relation.rel.through:
                    sub_objs = relation.bulk_related_objects(new_objs, self.using)
                    self.collect(sub_objs,
                                 source=model,
                                 source_attr=relation.rel.related_name,
                                 nullable=True)

    if collect_related:
        # Lookup for related objects with no remaining m2m relations
        for related in model._meta.get_all_related_many_to_many_objects():
            field = related.field
            if hasattr(related.model, 'delete_out_of_m2m') and field in related.model.delete_out_of_m2m:
                sub_objs = self.m2m_related_objects(related, new_objs, all_dependencies)
                if not sub_objs:
                    continue
                CASCADE(self, field, sub_objs, self.using)

        # Lookup for related objects that will be deleted in a custom way (signals or overriding save/delete method)
        for obj in new_objs:
            related_collection = {}
            collect_related_objects_to_delete.send(object=obj, related_collection=related_collection, sender=obj.__class__)
            for model in related_collection.keys():
                if related_collection[model]:
                    related_collection[model][0].virtual_field = obj
                    CASCADE(self, VirtualField(model), related_collection[model], self.using)            

def m2m_related_objects(self, related, objs, all_dependencies):
    """ deletes contains the related objects with no remaining M2M relations to objs """
    deletable = []
    for related_object in self.related_objects(related, objs):
        if all_dependencies or not (set(getattr(related_object, related.field.name).all()) - set(objs)):
            deletable.append(related_object)
    return deletable

Collector.collect = m2m_collect
Collector.m2m_related_objects = m2m_related_objects
