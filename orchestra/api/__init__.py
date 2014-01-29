from django.core.urlresolvers import NoReverseMatch

from rest_framework import views
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter

from ..utils import autodiscover as module_autodiscover


class OrchestraRouter(DefaultRouter):
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
        
        def insert_links(view, view_names):
            """ factory function """
            def inserted_links(self, request, view=view, *args, **kwargs):
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
            return inserted_links
        
        viewset.list = insert_links(viewset.list, ['api-root'])
        retrieve_links = ['api-root', '%s-list' % base_name]
        # Determine any `@action` or `@link` decorated methods on the viewset
        for methodname in dir(viewset):
            attr = getattr(viewset, methodname)
            if hasattr(attr, 'bind_to_methods'):
                retrieve_links.append('%s-%s' % (base_name, methodname))
        viewset.retrieve = insert_links(viewset.retrieve, retrieve_links)
        self.registry.append((prefix, viewset, base_name))
    
    def insert(self, prefix, name, field, **kwargs):
        """ Dynamically add new fields to an existing serializer """
        for _prefix, viewset, basename in self.registry:
            if _prefix == prefix:
                if viewset.serializer_class is None:
                    viewset.serializer_class = viewset().get_serializer_class()
                viewset.serializer_class.base_fields.update({name: field(**kwargs)})



# Create a router and register our viewsets with it.
router = OrchestraRouter()

autodiscover = lambda: (module_autodiscover('api'), module_autodiscover('serializers'))
