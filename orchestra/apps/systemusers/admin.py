from django.contrib import admin

from .models import SystemUser, SystemGroup


admin.site.register(SystemUser)
admin.site.register(SystemGroup)
