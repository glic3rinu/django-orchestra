from django.conf import settings

from orchestra.settings import BASE_DOMAIN


SAAS_ENABLED_SERVICES = getattr(settings, 'SAAS_ENABLED_SERVICES', (
    'orchestra.contrib.saas.services.moodle.MoodleService',
    'orchestra.contrib.saas.services.bscw.BSCWService',
    'orchestra.contrib.saas.services.gitlab.GitLabService',
    'orchestra.contrib.saas.services.phplist.PHPListService',
    'orchestra.contrib.saas.services.wordpress.WordPressService',
    'orchestra.contrib.saas.services.dokuwiki.DokuWikiService',
    'orchestra.contrib.saas.services.drupal.DrupalService',
    'orchestra.contrib.saas.services.seafile.SeaFileService',
))


SAAS_WORDPRESS_ADMIN_PASSWORD = getattr(settings, 'SAAS_WORDPRESSMU_ADMIN_PASSWORD',
    'secret'
)


SAAS_WORDPRESS_BASE_URL = getattr(settings, 'SAAS_WORDPRESS_BASE_URL',
    'http://blogs.{}/'.format(BASE_DOMAIN)
)


SAAS_DOKUWIKI_TEMPLATE_PATH = getattr(settings, 'SAAS_DOKUWIKI_TEMPLATE_PATH',
    '/home/httpd/htdocs/wikifarm/template.tar.gz'
)


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
    'lists.{}'.format(BASE_DOMAIN)
)


SAAS_SEAFILE_DOMAIN = getattr(settings, 'SAAS_SEAFILE_DOMAIN',
    'seafile.{}'.format(BASE_DOMAIN)
)


SAAS_SEAFILE_DEFAULT_QUOTA = getattr(settings, 'SAAS_SEAFILE_DEFAULT_QUOTA',
    50
)


SAAS_BSCW_DOMAIN = getattr(settings, 'SAAS_BSCW_DOMAIN',
    'bscw.{}'.format(BASE_DOMAIN)
)


SAAS_BSCW_DEFAULT_QUOTA = getattr(settings, 'SAAS_BSCW_DEFAULT_QUOTA',
    50
)

SAAS_BSCW_BSADMIN_PATH = getattr(settings, 'SAAS_BSCW_BSADMIN_PATH', 
    '/home/httpd/bscw/bin/bsadmin',
)


SAAS_GITLAB_ROOT_PASSWORD = getattr(settings, 'SAAS_GITLAB_ROOT_PASSWORD',
    'secret'
)


SAAS_GITLAB_DOMAIN = getattr(settings, 'SAAS_GITLAB_DOMAIN',
    'gitlab.{}'.format(BASE_DOMAIN)
)

