from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import insertattr
from orchestra.apps.users.roles.admin import RoleAdmin

from .models import POSIX


class POSIXRoleAdmin(RoleAdmin):
    model = POSIX
    name = 'posix'
    url_name = 'posix'


insertattr(get_user_model(), 'roles', POSIXRoleAdmin)
