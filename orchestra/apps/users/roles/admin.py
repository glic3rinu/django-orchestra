from django.contrib import messages
from django.contrib.admin.util import unquote, get_deleted_objects
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.core.urlresolvers import reverse
from django.db import router
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext, ugettext_lazy as _

from orchestra.admin.utils import get_modeladmin

from .forms import role_form_factory
from ..models import User


class RoleAdmin(object):
    model = None
    name = ''
    url_name = ''
    form = None
    
    def __init__(self, user=None):
        self.user = user
    
    @property
    def exists(self):
        try:
            return getattr(self.user, self.name)
        except self.model.DoesNotExist:
            return False
    
    def get_user(self, request, object_id):
        modeladmin = get_modeladmin(User)
        user = modeladmin.get_object(request, unquote(object_id))
        opts = self.model._meta
        if user is None:
            raise Http404(
                _('%(name)s object with primary key %(key)r does not exist.') %
                {'name': force_text(opts.verbose_name), 'key': escape(object_id)}
            )
        return user
    
    def change_view(self, request, object_id):
        modeladmin = get_modeladmin(User)
        user = self.get_user(request, object_id)
        self.user = user
        obj = None
        exists = self.exists
        if exists:
            obj = getattr(user, self.name)
        form_class = self.form if self.form else role_form_factory(self)
        form = form_class(instance=obj)
        opts = modeladmin.model._meta
        app_label = opts.app_label
        title = _("Add %s for user %s" % (self.name, user))
        action = _("Create")
        # User has submitted the form
        if request.method == 'POST':
            form = form_class(request.POST, instance=obj)
            form.user = user
            if form.is_valid():
                obj = form.save()
                context = {
                    'name': obj._meta.verbose_name,
                    'obj': obj,
                    'action': _("saved" if exists else "created")
                }
                modeladmin.log_change(request, request.user, "%s saved" % self.name.capitalize())
                msg = _('The role %(name)s for user "%(obj)s" was %(action)s successfully.') % context
                modeladmin.message_user(request, msg, messages.SUCCESS)
                url = 'admin:%s_%s_change' % (opts.app_label, opts.module_name)
                if not "_continue" in request.POST:
                    return redirect(url, object_id)
                exists = True
        
        if exists:
            title = _("Change %s %s settings" % (user, self.name))
            action = _("Save")
            form = form_class(instance=obj)
        
        context = {
            'title': title,
            'opts': opts,
            'app_label': app_label,
            'form': form,
            'action': action,
            'role': self,
            'roles': [ role(user=user) for role in modeladmin.roles ],
            'media': modeladmin.media
        }
        
        template = 'admin/users/user/role.html'
        app = modeladmin.admin_site.name
        return TemplateResponse(request, template, context, current_app=app)
    
    def delete_view(self, request, object_id):
        "The 'delete' admin view for this model."
        opts = self.model._meta
        app_label = opts.app_label
        modeladmin = get_modeladmin(User)
        user = self.get_user(request, object_id)
        obj = getattr(user, self.name)
        
        using = router.db_for_write(self.model)
        
        # Populate deleted_objects, a data structure of all related objects that
        # will also be deleted.
        (deleted_objects, perms_needed, protected) = get_deleted_objects(
            [obj], opts, request.user, modeladmin.admin_site, using)
        
        if request.POST:  # The user has already confirmed the deletion.
            if perms_needed:
                raise PermissionDenied
            obj_display = force_text(obj)
            modeladmin.log_deletion(request, obj, obj_display)
            modeladmin.delete_model(request, obj)
            post_url = reverse('admin:users_user_change', args=(user.pk,))
            preserved_filters = modeladmin.get_preserved_filters(request)
            post_url = add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts}, post_url
            )
            return HttpResponseRedirect(post_url)
        
        object_name = force_text(opts.verbose_name)
        
        if perms_needed or protected:
            title = _("Cannot delete %(name)s") % {"name": object_name}
        else:
            title = _("Are you sure?")
        
        context = {
            "title": title,
            "object_name": object_name,
            "object": obj,
            "deleted_objects": deleted_objects,
            "perms_lacking": perms_needed,
            "protected": protected,
            "opts": opts,
            "app_label": app_label,
            'preserved_filters': modeladmin.get_preserved_filters(request),
            'role': self,
        }
        return TemplateResponse(request, 'admin/users/user/delete_role.html',
                context, current_app=modeladmin.admin_site.name)
