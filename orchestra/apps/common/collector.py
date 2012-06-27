from common.signals import collect_dependencies
from django.db import models, router


def collect_related(instances):
    """ We assume that instances is a list of objects of the same model"""
    collector = models.deletion.Collector(using=router.db_for_write(instances[0].__class__))
    collector.collect(instances, all_dependencies=True)
    _instances = []
    for model, objects in collector.data.iteritems():
        for obj in objects:
            if obj not in instances:
                _instances.append(obj)
    return _instances


class DependencyCollector(object):
    """ 
        self.edge contains the first node of an "acyclic direct graph". 
        each parent could be another node or a list of nodes.
        parents = [ node1, [node2, node3, node4], node5]
        which means: (node1 OR (node2 AND node3 AND node4) OR node5)
        self.objects contains the same information but disposed as a dictionary: 
        {'obj1': [parent1, parent2,]}
        weak=True means that all dependencies will be delivered (weak relation/dependency: deleted or not deleted)
        weak=False menas that only are counted as a dependency the objects that strongly 
                   depends on it. ex: those will trigger a delete on cascade.
        Two extra attributes are able to use on models:
            * delete_out_of_m2m: with will be collected as an strong AND denendency
            * follow_m2m: with will be followed on weak dependency introspection
    """
    class Node(object):
        def __init__(self, content):
            self.content = content
            self.parents = []
            self.path = []

        def __repr__(self):
            return "%s:%s" % (self.content.__class__.__name__, self.content)
             
    def __init__(self, obj, weak=False):
        self.weak = weak
        self.objects = {}
        self.edge = self.dependency_lookup(obj)

    def dependency_lookup(self, obj):
        #TODO cache prefetch with select_related() ? 
#        obj.__class__._default_manager.select_related().get(pk=obj.pk)
        return self._rec_dependency_lookup(obj, [obj])

    def _rec_dependency_lookup(self, obj, path):
        node = self.Node(content=obj)
        # FK 
        for field in obj._meta.fields:
            if hasattr(field, 'related') and (self.weak or not field.null):
                related_object = getattr(obj, field.name)
                if related_object and related_object not in path:
                    #TODO: dry this 3line pice?
                    new_path = list(path+[related_object])
                    parent = self._rec_dependency_lookup(related_object, new_path)
                    node.parents.append(parent)
                #TODO GFK with GenericRelated (means that it must popup when weak=False)
                #TODO make it more generic: now it only works if GFK accessor is content_object attribute
                if self.weak and field.name == 'content_type' and hasattr(obj, 'content_object'):
                    related_object = getattr(obj, 'content_object')
                    if related_object and related_object not in path:
                        new_path = list(path+[related_object])
                        parent = self._rec_dependency_lookup(related_object, new_path)
                        node.parents.append(parent)                        
        # M2M
        model = obj.__class__
        m2m_fields = []
        if hasattr(model, 'delete_out_of_m2m'):
            m2m_fields = model.delete_out_of_m2m
        if self.weak and hasattr(model, 'follow_m2m'):
            for field in model.follow_m2m:
                if not field in m2m_fields: m2m_fields.append(field)
        for field in m2m_fields:
            and_nodes = []
            for related_object in getattr(obj, field.name).all():
                if related_object not in path:
                    new_path = list(path+[related_object])                    
                    parent = self._rec_dependency_lookup(related_object, new_path)
                    and_nodes.append(parent)
            node.parents.append(and_nodes)

        # Inherited models Parent -> Soon lookup 
        for related in obj._meta.get_all_related_objects():
            model = related.model
            for parent_model, ptr in related.opts.parents.iteritems():
                sons = model._base_manager.filter(**{"%s" % ptr.name: obj})
                for son in sons:
                    if son not in path:
                        new_path = list(path+[son])
                        parent = self._rec_dependency_lookup(son, new_path)
                        node.parents.append(parent)

        #TODO implement weak concept on collect_dependencies
        # VirtualRelations
        collected = []
        collect_dependencies.send(sender=obj.__class__, object=obj, collection=collected)
        for related_object in collected:
            if isinstance(related_object, list):
                collected += related_object
            if related_object not in path: 
                new_path = list(path+[related_object])            
                parent = self._rec_dependency_lookup(related_object, new_path)
                node.parents.append(parent)

        self.objects[obj]=node.parents
        return node
