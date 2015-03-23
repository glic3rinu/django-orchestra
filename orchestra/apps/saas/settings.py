from django.conf import settings


SAAS_ENABLED_SERVICES = getattr(settings, 'SAAS_ENABLED_SERVICES', (
    'orchestra.apps.saas.services.moodle.MoodleService',
    'orchestra.apps.saas.services.bscw.BSCWService',
    'orchestra.apps.saas.services.gitlab.GitLabService',
    'orchestra.apps.saas.services.phplist.PHPListService',
    'orchestra.apps.saas.services.wordpress.WordPressService',
    'orchestra.apps.saas.services.dokuwiki.DokuWikiService',
    'orchestra.apps.saas.services.drupal.DrupalService',
))


SAAS_WORDPRESS_ADMIN_PASSWORD = getattr(settings, 'SAAS_WORDPRESSMU_ADMIN_PASSWORD',
    'secret'
)

SAAS_WORDPRESS_BASE_URL = getattr(settings, 'SAAS_WORDPRESS_BASE_URL',
    'http://blogs.orchestra.lan/'
)


SAAS_DOKUWIKI_TEMPLATE_PATH = getattr(settings, 'SAAS_DOKUWIKI_TEMPLATE_PATH',
    '/home/httpd/htdocs/wikifarm/template.tar.gz')

SAAS_DOKUWIKI_FARM_PATH = getattr(settings, 'WEBSITES_DOKUWIKI_FARM_PATH',
    '/home/httpd/htdocs/wikifarm/farm'
)

SAAS_DRUPAL_SITES_PATH = getattr(settings, 'WEBSITES_DRUPAL_SITES_PATH',
    '/home/httpd/htdocs/drupal-mu/sites/%(site_name)s'
)


SAAS_PHPLIST_DB_NAME = getattr(settings, 'SAAS_PHPLIST_DB_NAME',
    'phplist_mu'
)

SAAS_PHPLIST_BASE_DOMAIN = getattr(settings, 'SAAS_PHPLIST_BASE_DOMAIN',
    'lists.orchestra.lan'
)


SAAS_BSCW_DOMAIN = getattr(settings, 'SAAS_BSCW_DOMAIN',
    'bscw.orchestra.lan'
)


