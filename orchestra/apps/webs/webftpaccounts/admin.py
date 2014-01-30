from django.contrib import admin

from orchestra.admin.utils import insertattr

from .models import WebFTPAccount
from ..models import Web


class WebFTPAccountInline(admin.TabularInline):
    model = WebFTPAccount


insertattr(Web, 'inlines', WebFTPAccountInline)
