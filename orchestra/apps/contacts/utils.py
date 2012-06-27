import django
from datetime import datetime
from contacts.models import Contact, Contract
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

def get_child(obj):
    result = None
    if hasattr(obj, 'get_base_service_child'):
        result = obj.get_base_service_child()
    if not result:  return obj
    return result


def get_related(obj):
    """Returns the related objects of an object, i.e. all the objects that are 
    subject to be deleted when obj is deleted""" 
    related_list = []
    attribute_name = []
    if type(obj) is tuple:
        return zip(related_list, attribute_name)
    if type(obj) is Contact:
        ct = ContentType.objects.get_for_model(obj)
        contracts = Contract.objects.filter(Q(contact=obj) & ~Q(content_type=ct, object_id=obj.pk))
        print contracts.values_list('pk', flat=True)
        for c in contracts:
            shared = False
            attribute_name.append('contact')
            try:
                shared = c.content_object.is_shared
            except AttributeError:
                pass
            if shared:
                related_list.append((c.content_object, obj))
            else:
                related_list.append(c.content_object)
        return zip(related_list, attribute_name)

    #get FK:
    for related in obj._meta.get_all_related_objects():
        model = related.model
        field = related.field
        if not field.null:
            for rel_object in model.objects.filter(**{'%s' % (field.name): obj}):
                rel_object = get_child(rel_object)
                related_list.append(rel_object)
                attribute_name.append(field.name)

    #get M2M:
    for related in obj._meta.get_all_related_many_to_many_objects():
        field = related.field
        model = related.model
        if not field.null:
            rel_objects = getattr(obj, '%s_set' % (model.__name__.lower())).all()
            for rel_object in rel_objects:
                rel_object = get_child(rel_object)
                related_list.append(rel_object)
                attribute_name.append(field.name)
    result = zip(related_list, attribute_name)
    return result


def get_depends_on(obj):
    """Returns a list of lists with the objects that obj depends_on, i.e. if all
    the elements in one of the lists are canceled, then obj should be canceled
    too"""
    #TODO should be updated for the Contacts case
    result = []
    # FK
    for field in obj._meta.fields:
        _result = []
        if field.__class__ is django.db.models.fields.related.ForeignKey or field.__class__ is django.db.models.fields.related.OneToOneField:
            if not field.null:
                rel = getattr(obj, field.name)
                _result.append(rel)
        if _result: result.append(_result)
    # M2M
    for field in obj._meta.local_many_to_many:
        _result = []
        if not field.null:
            for rel in getattr(obj, field.name).all():
                _result.append(rel)
        if _result: result.append(_result)

    return result


