from .options import SoftwareService


class DokuWikiService(SoftwareService):
    name = 'dokuwiki'
    verbose_name = "Dowkuwiki"
    icon = 'orchestra/icons/apps/Dokuwiki.png'
    
    @property
    def site_base_domain(self):
        from .. import settings
        return settings.SAAS_DOKUWIKI_BASE_DOMAIN
