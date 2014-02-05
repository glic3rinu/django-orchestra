from . import settings


class Node(object):
    def __init__(self, content):
        self.content = content
        self.parents = []
        self.path = []
    
    def __repr__(self):
        return "%s:%s" % (type(self.content).__name__, self.content)


class Collector(object):
    def __init__(self, obj, cascade_only=False):
        self.obj = obj
        self.cascade_only = cascade_only
    
    def collect(self):
        depth = settings.ORDERS_COLLECTOR_MAX_DEPTH
        return self._rec_collect(self.obj, [self.obj], depth)
    
    def _rec_collect(self, obj, path, depth):
        node = Node(content=obj)
        # FK lookups
        for field in obj._meta.fields:
            if hasattr(field, 'related') and (self.cascade_only or not field.null):
                related_object = getattr(obj, field.name)

