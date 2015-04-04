from django.conf import settings as django_settings
from django.utils.module_loading import autodiscover_modules
from rest_framework.routers import DefaultRouter

from orchestra import settings
from orchestra.utils.python import import_class

from .helpers import insert_links


class LinkHeaderRouter(DefaultRouter):
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
router = LinkHeaderRouter(trailing_slash=django_settings.APPEND_SLASH)

autodiscover = lambda: (autodiscover_modules('api'), autodiscover_modules('serializers'))
