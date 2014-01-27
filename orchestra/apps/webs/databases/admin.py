from django.contrib import admin

from orchestra.admin.utils import insertattr

from .models import Database
from ..models import Web


class DatabaseInline(admin.TabularInline):
    model = Database


insertattr(Web, 'inlines', DatabaseInline)
