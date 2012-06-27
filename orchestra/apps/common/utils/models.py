from django.db import models


def generate_chainer_manager(qs_class):
    # Allow chained managers
    # Based on http://djangosnippets.org/snippets/562/#c2486
    class ChainerManager(models.Manager):
        def __init__(self):
            super(ChainerManager,self).__init__()
            self.queryset_class = qs_class

        def get_query_set(self):
            return self.queryset_class(self.model)

        def __getattr__(self, attr, *args):
            try:
                return getattr(self.__class__, attr, *args)
            except AttributeError:
                return getattr(self.get_query_set(), attr, *args)
    return ChainerManager()


def group_by(cls, field, objects, dictionary=False, queryset=True):
    """ 
        input can be a queryset or a list
        field: the model field do you want to group_by suport indirect fields like 'contact__service'
        return [group, [g_objects_qset],]
        if queryset=False: return list of objects insted ad queryset (performance booster)
        if dictionary=True: return {group: [g_objects_qset]}
    """
    grouped_objects = {} if dictionary else []
    if not objects: return grouped_objects
    if cls == list:
        for obj in objects:
            field_sorted = obj
            if field == '__class__': field_sorted = getattr(field_sorted, field)
            else: 
                for _field in field.split('__'):
                    field_sorted = getattr(field_sorted, _field)
            if dictionary:
                if grouped_objects.has_key(field_sorted):
                    grouped_objects[field_sorted].append(obj)
                else: grouped_objects[field_sorted] = [obj]
            else: raise AttributeError('not implemented')
        return grouped_objects
    else:
        ant = None
        for obj in objects.order_by(field):
            field_sorted = obj
            for _field in field.split('__'):
                field_sorted = getattr(field_sorted, _field)
            if field_sorted == ant:
                if queryset: group.append(obj.pk)
                else: group.append(obj)
            else:
                if ant:
                    if queryset: group=cls.objects.filter(pk__in=group)
                    if dictionary: grouped_objects[ant]=group
                    else: grouped_objects.append([ant, group])
                if queryset: group = [obj.pk]
                else: group = [obj]
            ant = field_sorted
        if queryset: group=cls.objects.filter(pk__in=group)   
        if dictionary: grouped_objects[ant] = group  
        else: grouped_objects.append([ant, group])
        return grouped_objects


def has_changed(instance, field):
    if not instance.pk:
        return False
    old_value = instance.__class__._default_manager.\
             filter(pk=instance.pk).values(field).get()[field]
    return not getattr(instance, field) == old_value


class VirtualField(object):
    """ a fake field needed on common.models.Collector for custom deletes """
    class VirtualRelated(object):
        def __init__(self, model):
            self.model = model
            
        @property
        def to(self):
            return self.model

    def __init__(self, model):
        self.model = model

    @property
    def rel(self):
        a = self.VirtualRelated(self.model)
        return a
    
    @property
    def name(self):
        return 'virtual_field'
    
    @property
    def null(self):
        return False

