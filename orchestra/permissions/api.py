from django.core.urlresolvers import resolve
from rest_framework.permissions import DjangoModelPermissions


class OrchestraPermissionBackend(DjangoModelPermissions):
    """ Permissions according to each user """
    
    def has_permission(self, request, view):
        queryset = getattr(view, 'queryset', None)
        if queryset is None:
            name = resolve(request.path).url_name
            return name == 'api-root'
        
        model_cls = queryset.model
        perms = self.get_required_permissions(request.method, model_cls)
        if (request.user and
            request.user.is_authenticated() and
            request.user.has_perms(perms, model_cls)):
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        perms = self.get_required_permissions(request.method, type(obj))
        if (request.user and
            request.user.is_authenticated() and
            request.user.has_perms(perms, obj)):
            return True
        return False
