import functools
import inspect


# WARNING: *MAGIC MODULE*
# This is not a safe place, lot of magic is happening here


class Permission(object):
    """ 
    Base class used for defining class and instance permissions.
    Enabling an ''intuitive'' interface for checking permissions:
        
        # Define permissions
        class NodePermission(Permission):
            def change(self, obj, cls, user):
                return obj.user == user
        
        # Provide permissions
        Node.has_permission = NodePermission()
        
        # Check class permission by passing it as string
        Node.has_permission(user, 'change')
        
        # Check class permission by calling it
        Node.has_permission.change(user)
        
        # Check instance permissions
        node = Node()
        node.has_permission(user, 'change')
        node.has_permission.change(user)
    """
    def __get__(self, obj, cls):
        """ Hacking object internals to provide means for the mentioned interface """
        # call interface: has_permission(user, 'perm')
        def call(user, perm):
            return getattr(self, perm)(obj, cls, user)
        
        # has_permission.perm(user)
        for func in inspect.getmembers(type(self), predicate=inspect.ismethod):
            if not isinstance(self, func[1].__self__.__class__):
                # aggregated methods
                setattr(call, func[0], functools.partial(func[1], obj, cls))
            else:
                # self methods
                setattr(call, func[0], functools.partial(func[1], self, obj, cls))
        return call
    
    def _aggregate(self, obj, cls, perm):
        """ Aggregates cls methods to self class"""
        for method in inspect.getmembers(perm, predicate=inspect.ismethod):
            if not method[0].startswith('_'):
                setattr(type(self), method[0], method[1])


class ReadOnlyPermission(Permission):
    """ Read only permissions """
    def view(self, obj, cls, user):
        return True


class AllowAllPermission(object):
    """ All methods return True """
    def __get__(self, obj, cls):
        return self.AllowAllWrapper()

    class AllowAllWrapper(object):
        """ Fake object that always returns True """
        def __call__(self, *args):
            return True
        
        def __getattr__(self, name):
            return lambda n: True


class RelatedPermission(Permission):
    """
    Inherit permissions of a related object
    
    The following example will inherit permissions from sliver_iface.sliver.slice
        SliverIfaces.has_permission = RelatedPermission('sliver.slices')
    """
    def __init__(self, relation):
        self.relation = relation
    
    def __get__(self, obj, cls):
        """ Hacking object internals to provide means for the mentioned interface """
        # Walk through FK relations
        relations = self.relation.split('.')
        if obj is None:
            parent = cls
            for relation in relations:
                parent = getattr(parent, relation).field.rel.to
        else:
            parent = functools.reduce(getattr, relations, obj)
        
        # call interface: has_permission(user, 'perm')
        def call(user, perm):
            return parent.has_permission(user, perm)
        
        # method interface: has_permission.perm(user)
        for name, func in parent.has_permission.__dict__.items():
            if not name.startswith('_'):
                setattr(call, name, func)
        
        return call
