from orchestra.contrib.settings import Setting
from orchestra.settings import ORCHESTRA_BASE_DOMAIN

from .. import saas


SAAS_ENABLED_SERVICES = Setting('SAAS_ENABLED_SERVICES',
    (
        'orchestra.contrib.saas.services.moodle.MoodleService',
        'orchestra.contrib.saas.services.bscw.BSCWService',
        'orchestra.contrib.saas.services.gitlab.GitLabService',
        'orchestra.contrib.saas.services.phplist.PHPListService',
        'orchestra.contrib.saas.services.wordpress.WordPressService',
        'orchestra.contrib.saas.services.dokuwiki.DokuWikiService',
        'orchestra.contrib.saas.services.drupal.DrupalService',
        'orchestra.contrib.saas.services.seafile.SeaFileService',
    ),
    # lazy loading
    choices=lambda: ((s.get_class_path(), s.get_class_path()) for s in saas.services.SoftwareService.get_plugins()),
    multiple=True,
)


SAAS_WORDPRESS_ADMIN_PASSWORD = Setting('SAAS_WORDPRESSMU_ADMIN_PASSWORD',
    'secret'
)


SAAS_WORDPRESS_BASE_URL = Setting('SAAS_WORDPRESS_BASE_URL',
    'https://blogs.{}/'.format(ORCHESTRA_BASE_DOMAIN),
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default.",
)


SAAS_DOKUWIKI_TEMPLATE_PATH = Setting('SAAS_DOKUWIKI_TEMPLATE_PATH',
    '/home/httpd/htdocs/wikifarm/template.tar.gz'
)


SAAS_DOKUWIKI_FARM_PATH = Setting('WEBSITES_DOKUWIKI_FARM_PATH',
    '/home/httpd/htdocs/wikifarm/farm'
)


SAAS_DRUPAL_SITES_PATH = Setting('WEBSITES_DRUPAL_SITES_PATH',
    '/home/httpd/htdocs/drupal-mu/sites/%(site_name)s',
    
)


SAAS_PHPLIST_DB_NAME = Setting('SAAS_PHPLIST_DB_NAME',
    'phplist_mu',
)


SAAS_PHPLIST_BASE_DOMAIN = Setting('SAAS_PHPLIST_BASE_DOMAIN',
    'lists.{}'.format(ORCHESTRA_BASE_DOMAIN),
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default.",
)


SAAS_SEAFILE_DOMAIN = Setting('SAAS_SEAFILE_DOMAIN',
    'seafile.{}'.format(ORCHESTRA_BASE_DOMAIN),
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default.",
)


SAAS_SEAFILE_DEFAULT_QUOTA = Setting('SAAS_SEAFILE_DEFAULT_QUOTA',
    50
)


SAAS_BSCW_DOMAIN = Setting('SAAS_BSCW_DOMAIN',
    'bscw.{}'.format(ORCHESTRA_BASE_DOMAIN),
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default.",
)


SAAS_BSCW_DEFAULT_QUOTA = Setting('SAAS_BSCW_DEFAULT_QUOTA',
    50,
)


SAAS_BSCW_BSADMIN_PATH = Setting('SAAS_BSCW_BSADMIN_PATH', 
    '/home/httpd/bscw/bin/bsadmin',
)


SAAS_GITLAB_ROOT_PASSWORD = Setting('SAAS_GITLAB_ROOT_PASSWORD',
    'secret',
)


SAAS_GITLAB_DOMAIN = Setting('SAAS_GITLAB_DOMAIN',
    'gitlab.{}'.format(ORCHESTRA_BASE_DOMAIN),
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default.",
)
