from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import autodiscover_modules
from rest_framework.routers import DefaultRouter, Route, flatten, replace_methodname

from orchestra import settings
#from orchestra.utils.apps import autodiscover as module_autodiscover
from orchestra.utils.python import import_class

from .helpers import insert_links, replace_collectionmethodname


def collectionlink(**kwargs):
    """
    Used to mark a method on a ViewSet collection that should be routed for GET requests.
    """
    # TODO deprecate in favour of DRF2.0 own method
    def decorator(func):
        func.collection_bind_to_methods = ['get']
        func.kwargs = kwargs
        return func
    return decorator


class LinkHeaderRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        """ collection view method route """
        super(LinkHeaderRouter, self).__init__(*args, **kwargs)
        self.routes.insert(0, Route(
            url=r'^{prefix}/{collectionmethodname}{trailing_slash}$',
            mapping={
                '{httpmethod}': '{collectionmethodname}',
            },
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ))
    
    def get_routes(self, viewset):
        """ allow links and actions to be bound to a collection view """
        known_actions = flatten([route.mapping.values() for route in self.routes])
        dynamic_routes = []
        collection_dynamic_routes = []
        for methodname in dir(viewset):
            attr = getattr(viewset, methodname)
            bind = getattr(attr, 'bind_to_methods', None)
            httpmethods = getattr(attr, 'collection_bind_to_methods', bind)
            if httpmethods:
                if methodname in known_actions:
                    msg = ('Cannot use @action or @link decorator on method "%s" '
                           'as it is an existing route' % methodname)
                    raise ImproperlyConfigured(msg)
                httpmethods = [method.lower() for method in httpmethods]
                if bind:
                    dynamic_routes.append((httpmethods, methodname))
                else:
                    collection_dynamic_routes.append((httpmethods, methodname))
        
        ret = []
        for route in self.routes:
            # Dynamic routes (@link or @action decorator)
            if route.mapping == {'{httpmethod}': '{methodname}'}:
                replace = replace_methodname
                routes = dynamic_routes
            elif route.mapping == {'{httpmethod}': '{collectionmethodname}'}:
                replace = replace_collectionmethodname
                routes = collection_dynamic_routes
            else:
                ret.append(route)
                continue
            for httpmethods, methodname in routes:
                initkwargs = route.initkwargs.copy()
                initkwargs.update(getattr(viewset, methodname).kwargs)
                ret.append(Route(
                    url=replace(route.url, methodname),
                    mapping={ httpmethod: methodname for httpmethod in httpmethods },
                    name=replace(route.name, methodname),
                    initkwargs=initkwargs,
                ))
        return ret
    
    def get_api_root_view(self):
        """ returns the root view, with all the linked collections """
        APIRoot = import_class(settings.API_ROOT_VIEW)
        APIRoot.router = self
        return APIRoot.as_view()
    
    def register(self, prefix, viewset, base_name=None):
        """ inserts link headers on every viewset """
        if base_name is None:
            base_name = self.get_default_base_name(viewset)
        insert_links(viewset, base_name)
        self.registry.append((prefix, viewset, base_name))
    
    def get_viewset(self, prefix_or_model):
        for _prefix, viewset, __ in self.registry:
            if _prefix == prefix_or_model or viewset.model == prefix_or_model:
                return viewset
        msg = "%s does not have a regiestered viewset" % prefix_or_model
        raise KeyError(msg)
        
    def insert(self, prefix_or_model, name, field, **kwargs):
        """ Dynamically add new fields to an existing serializer """
        viewset = self.get_viewset(prefix_or_model)
#        setattr(viewset, 'inserted', getattr(viewset, 'inserted', []))
        if viewset.serializer_class is None:
            viewset.serializer_class = viewset().get_serializer_class()
        viewset.serializer_class.base_fields.update({name: field(**kwargs)})
#        if not name in viewset.inserted:
        viewset.serializer_class.Meta.fields += (name,)
#            viewset.inserted.append(name)


# Create a router and register our viewsets with it.
router = LinkHeaderRouter()

autodiscover = lambda: (autodiscover_modules('api'), autodiscover_modules('serializers'))
