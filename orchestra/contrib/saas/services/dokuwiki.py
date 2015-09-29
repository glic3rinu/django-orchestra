from .options import SoftwareService
from .. import settings


class DokuWikiService(SoftwareService):
    name = 'dokuwiki'
    verbose_name = "Dowkuwiki"
    icon = 'orchestra/icons/apps/Dokuwiki.png'
    site_domain = settings.SAAS_DOKUWIKI_DOMAIN
