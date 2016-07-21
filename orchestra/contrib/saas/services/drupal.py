from .options import SoftwareService

from .. import settings


class DrupalService(SoftwareService):
    name = 'drupal'
    verbose_name = "Drupal"
    icon = 'orchestra/icons/apps/Drupal.png'
    site_domain = settings.SAAS_DRUPAL_DOMAIN
