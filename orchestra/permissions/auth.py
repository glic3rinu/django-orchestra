from django.contrib.auth.backends import ModelBackend
from django.apps import apps


class OrchestraPermissionBackend(ModelBackend):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False
    
    def has_perm(self, user, perm, obj=None):
        """ perm 'app.action_model' """
        if not user.is_active:
            return False
        
        perm_type = perm.split('.')[1].split('_')[0]
        if obj is None:
            app_label = perm.split('.')[0]
            model_label = perm.split('_')[1]
            model = apps.get_model(app_label, model_label)
            perm_manager = model
        else:
            perm_manager = obj
        
        try: 
            is_authorized = perm_manager.has_permission(user, perm_type)
        except AttributeError:
            is_authorized = False
        
        return is_authorized
    
    def has_module_perms(self, user, app_label):
        """
        Returns True if user_obj has any permissions in the given app_label.
        """
        if not user.is_active:
            return False
        app = apps.get_app_config(app_label)
        for model in apps.get_models(app):
            try:
                has_perm = model.has_permission.view(user)
            except AttributeError:
                pass
            else:
                if has_perm:
                    return True
        return False
