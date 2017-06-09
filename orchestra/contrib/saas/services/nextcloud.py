from django import forms
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .. import settings
from .options import SoftwareService


class NextCloudService(SoftwareService):
    name = 'nextcloud'
    verbose_name = "nextCloud"
    icon = 'orchestra/icons/apps/nextCloud.png'
    site_domain = settings.SAAS_NEXTCLOUD_DOMAIN
