from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .options import SoftwareService
from .. import settings


class DokuWikiService(SoftwareService):
    name = 'dokuwiki'
    verbose_name = "Dowkuwiki"
    icon = 'orchestra/icons/apps/Dokuwiki.png'
    site_domain = settings.SAAS_DOKUWIKI_DOMAIN
    allow_custom_url = settings.SAAS_DOKUWIKI_ALLOW_CUSTOM_URL
    
    def clean(self):
        if self.allow_custom_url and self.instance.custom_url:
            url = urlparse(self.instance.custom_url)
            if url.path and url.path != '/':
                raise ValidationError({
                    'custom_url': _("Support for specific URL paths (%s) is not implemented.") % url.path
                })
        super(DokuWikiService, self).clean()
