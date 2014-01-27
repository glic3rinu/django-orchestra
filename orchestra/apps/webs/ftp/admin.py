from django.contrib import admin

from orchestra.admin.utils import insertattr

from .models import FTP
from ..models import Web


class FTPInline(admin.TabularInline):
    model = FTP


insertattr(Web, 'inlines', FTPInline)
