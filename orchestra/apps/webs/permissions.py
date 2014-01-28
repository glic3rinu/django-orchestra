from orchestra.permissions import Permission

from .models import Web


class WebPermission(Permission):
    def view(self, obj, cls, user):
        return obj and obj.user is user
    
    def add(self, obj, cls, user):
        return user.is_staff
    
    def change(self, obj, cls, user):
        return self.view(obj, cls, user)
    
    def delete(self, obj, cls, user):
        return self.view(obj, cls, user)


Web.has_permission = WebPermission()
