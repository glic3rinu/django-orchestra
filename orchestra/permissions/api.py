from rest_framework import exceptions
from rest_framework.permissions import DjangoModelPermissions


class OrchestraPermissionBackend(DjangoModelPermissions):
    """ Permissions according to each user """
    
    def has_permission(self, request, view):
        model_cls = getattr(view, 'model', None)
        if not model_cls:
            return request.user.is_authenticated()
        
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
