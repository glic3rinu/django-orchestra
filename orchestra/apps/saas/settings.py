from django.conf import settings


SAAS_ENABLED_SERVICES = getattr(settings, 'SAAS_ENABLED_SERVICES', (
    'orchestra.apps.saas.services.wordpress.WordpressService',
    'orchestra.apps.saas.services.drupal.DrupalService',
    'orchestra.apps.saas.services.dokuwiki.DokuwikiService',
    'orchestra.apps.saas.services.moodle.MoodleService',
    'orchestra.apps.saas.services.bscw.BSCWService',
    'orchestra.apps.saas.services.gitlab.GitLabService',
    'orchestra.apps.saas.services.phplist.PHPListService',
))


SAAS_WORDPRESSMU_BASE_URL = getattr(settings, 'SAAS_WORDPRESSMU_BASE_URL',
    'http://%(site_name)s.example.com')


SAAS_WORDPRESSMU_ADMIN_PASSWORD = getattr(settings, 'SAAS_WORDPRESSMU_ADMIN_PASSWORD',
    'secret')


SAAS_DOKUWIKIMU_TEMPLATE_PATH = setattr(settings, 'SAAS_DOKUWIKIMU_TEMPLATE_PATH',
    '/home/httpd/htdocs/wikifarm/template.tar.gz')


SAAS_DOKUWIKIMU_FARM_PATH = getattr(settings, 'SAAS_DOKUWIKIMU_FARM_PATH',
    '/home/httpd/htdocs/wikifarm/farm')


SAAS_DRUPAL_SITES_PATH = getattr(settings, 'SAAS_DRUPAL_SITES_PATH',
    '/home/httpd/htdocs/drupal-mu/sites/%(site_name)s')
