from django.contrib import admin

from orchestra.admin.utils import insertattr

from .models import WebDatabase
from ..models import Web


class WebDatabaseInline(admin.TabularInline):
    model = WebDatabase


insertattr(Web, 'inlines', WebDatabaseInline)
