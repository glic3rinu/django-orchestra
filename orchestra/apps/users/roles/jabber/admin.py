from django.contrib.auth import get_user_model

from orchestra.admin.utils import insertattr
from orchestra.apps.users.roles.admin import RoleAdmin

from .models import Jabber


class JabberRoleAdmin(RoleAdmin):
    model = Jabber
    name = 'jabber'
    url_name = 'jabber'


insertattr(get_user_model(), 'roles', JabberRoleAdmin)
