from django import forms
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .. import settings
from .options import SoftwareService


class OwnCloudService(SoftwareService):
    name = 'owncloud'
    verbose_name = "ownCloud"
    icon = 'orchestra/icons/apps/ownCloud.png'
    site_domain = settings.SAAS_OWNCLOUD_DOMAIN
