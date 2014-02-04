from django.core.urlresolvers import NoReverseMatch

from rest_framework import views
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter, Route, flatten, replace_methodname

from .utils import autodiscover as module_autodiscover


def replace_listmethodname(format_string, methodname):
    ret = replace_methodname(format_string, methodname)
    ret = ret.replace('{listmethodname}', methodname)
    return ret


def list_link(**kwargs):
    """
    Used to mark a method on a ViewSet that should be routed for GET requests.
    """
    def decorator(func):
        func.list_bind_to_methods = ['get']
        func.kwargs = kwargs
        return func
    return decorator


class LinkHeaderRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        """ list view method route """
        super(LinkHeaderRouter, self).__init__(*args, **kwargs)
        self.routes.append(Route(
            url=r'^{prefix}/{listmethodname}{trailing_slash}$',
            mapping={
                '{httpmethod}': '{listmethodname}',
            },
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ))
    
    def get_routes(self, viewset):
        """ allow links and actions to be bind to a list view """
        known_actions = flatten([route.mapping.values() for route in self.routes])
        list_routes = []
        for methodname in dir(viewset):
            attr = getattr(viewset, methodname)
            httpmethods = getattr(attr, 'list_bind_to_methods', None)
            if httpmethods:
                if methodname in known_actions:
                    raise ImproperlyConfigured('Cannot use @action or @link decorator on '
                                               'method "%s" as it is an existing route' % methodname)
                httpmethods = [method.lower() for method in httpmethods]
                list_routes.append((httpmethods, methodname))
        ret = []
        for route in self.routes:
            if route.mapping == {'{httpmethod}': '{listmethodname}'}:
                # Dynamic routes (@link or @action decorator)
                for httpmethods, methodname in list_routes:
                    initkwargs = route.initkwargs.copy()
                    initkwargs.update(getattr(viewset, methodname).kwargs)
                    ret.append(Route(
                        url=replace_listmethodname(route.url, methodname),
                        mapping=dict((httpmethod, methodname) for httpmethod in httpmethods),
                        name=replace_listmethodname(route.name, methodname),
                        initkwargs=initkwargs,
                    ))
        # list methods goes first on the url definition
        return ret + super(LinkHeaderRouter, self).get_routes(viewset)
    
    def get_api_root_view(self):
        """ returns the root view, with all the linked collections """
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
        
        class APIRoot(views.APIView):
            def get(self, request, format=None):
                url = reverse('api-root', request=request, format=format)
                links = ['<%s>; rel="%s"' % (url, 'api-root')]
                for key, url_name in api_root_dict.items():
                    url = reverse(url_name, request=request, format=format)
                    links.append('<%s>; rel="%s"' % (url, url_name))
                headers = { 'Link': ', '.join(links) }
                return Response(None, headers=headers)
        
        return APIRoot.as_view()
    
    def register(self, prefix, viewset, base_name=None):
        """ inserts link headers on every viewset """
        if base_name is None:
            base_name = self.get_default_base_name(viewset)
        
        def insert_links_factory(view, view_names):
            def insert_links(self, request, view=view, *args, **kwargs):
                """ wrapper function that inserts HTTP links on view """
                links = []
                for name in view_names:
                    try:
                        url = reverse(name, request=request)
                    except NoReverseMatch:
                        url = reverse(name, args, kwargs, request=request)
                    links.append('<%s>; rel="%s"' % (url, name))
                response = view(self, request, *args, **kwargs)
                response['Link'] = ', '.join(links)
                return response
            return insert_links
        
        list_links = ['api-root']
        retrieve_links = ['api-root', '%s-list' % base_name]
        # Determine any `@action` or `@link` decorated methods on the viewset
        for methodname in dir(viewset):
            attr = getattr(viewset, methodname)
            view_name = '%s-%s' % (base_name, methodname.replace('_', '-'))
            if hasattr(attr, 'list_bind_to_methods'):
                list_links.append(view_name)
                retrieve_links.append(view_name)
            if hasattr(attr, 'bind_to_methods'):
                retrieve_links.append(view_name)
        viewset.list = insert_links_factory(viewset.list, list_links)
        viewset.retrieve = insert_links_factory(viewset.retrieve, retrieve_links)
        self.registry.append((prefix, viewset, base_name))
    
    def insert(self, prefix, name, field, **kwargs):
        """ Dynamically add new fields to an existing serializer """
        for _prefix, viewset, basename in self.registry:
            if _prefix == prefix:
                if viewset.serializer_class is None:
                    viewset.serializer_class = viewset().get_serializer_class()
                viewset.serializer_class.base_fields.update({name: field(**kwargs)})



# Create a router and register our viewsets with it.
router = LinkHeaderRouter()

autodiscover = lambda: (module_autodiscover('api'), module_autodiscover('serializers'))
