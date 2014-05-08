from django import conf
from django.core.exceptions import ImproperlyConfigured
from rest_framework import views
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter, Route, flatten, replace_methodname

from .. import settings
from ..utils.apps import autodiscover as module_autodiscover
from .helpers import insert_links, replace_collectionmethodname


def collectionlink(**kwargs):
    """
    Used to mark a method on a ViewSet collection that should be routed for GET requests.
    """
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
        class APIRoot(views.APIView):
            def get(instance, request, format=None):
                root_url = reverse('api-root', request=request, format=format)
                token_url = reverse('api-token-auth', request=request, format=format)
                links = [
                    '<%s>; rel="%s"' % (root_url, 'api-root'),
                    '<%s>; rel="%s"' % (token_url, 'api-get-auth-token'),
                ]
                if not request.user.is_anonymous():
                    list_name = '{basename}-list'
                    detail_name = '{basename}-detail'
                    for prefix, viewset, basename in self.registry:
                        singleton_pk = getattr(viewset, 'singleton_pk', False)
                        if singleton_pk:
                            url_name = detail_name.format(basename=basename)
                            kwargs = { 'pk': singleton_pk(viewset(), request) }
                        else:
                            url_name = list_name.format(basename=basename)
                            kwargs = {}
                        url = reverse(url_name, request=request, format=format, kwargs=kwargs)
                        links.append('<%s>; rel="%s"' % (url, url_name))
                    # Add user link
                    url_name = detail_name.format(basename='user')
                    kwargs = { 'pk': request.user.pk }
                    url = reverse(url_name, request=request, format=format, kwargs=kwargs)
                    links.append('<%s>; rel="%s"' % (url, url_name))
                headers = { 'Link': ', '.join(links) }
                content = {
                    name: getattr(settings, name, None)
                        for name in ['SITE_NAME', 'SITE_VERBOSE_NAME']
                }
                content['INSTALLED_APPS'] = conf.settings.INSTALLED_APPS
                return Response(content, headers=headers)
        return APIRoot.as_view()
    
    def register(self, prefix, viewset, base_name=None):
        """ inserts link headers on every viewset """
        if base_name is None:
            base_name = self.get_default_base_name(viewset)
        insert_links(viewset, base_name)
        self.registry.append((prefix, viewset, base_name))
    
    def insert(self, prefix, name, field, **kwargs):
        """ Dynamically add new fields to an existing serializer """
        for _prefix, viewset, basename in self.registry:
            if _prefix == prefix:
                if viewset.serializer_class is None:
                    viewset.serializer_class = viewset().get_serializer_class()
                viewset.serializer_class.Meta.fields += (name,)
                viewset.serializer_class.base_fields.update({name: field(**kwargs)})
                setattr(viewset, 'inserted', getattr(viewset, 'inserted', []))
                viewset.inserted.append(name)


# Create a router and register our viewsets with it.
router = LinkHeaderRouter()

autodiscover = lambda: (module_autodiscover('api'), module_autodiscover('serializers'))
