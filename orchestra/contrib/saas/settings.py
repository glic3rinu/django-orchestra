from django.utils.translation import ugettext_lazy as _

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


SAAS_WORDPRESS_BASE_DOMAIN = Setting('SAAS_WORDPRESS_BASE_DOMAIN',
    'blogs.{}'.format(ORCHESTRA_BASE_DOMAIN),
)


SAAS_DOKUWIKI_TEMPLATE_PATH = Setting('SAAS_DOKUWIKI_TEMPLATE_PATH',
    '/home/httpd/htdocs/wikifarm/template.tar.gz'
)


SAAS_DOKUWIKI_FARM_PATH = Setting('WEBSITES_DOKUWIKI_FARM_PATH',
    '/home/httpd/htdocs/wikifarm/farm'
)


SAAS_DOKUWIKI_BASE_DOMAIN = Setting('SAAS_DOKUWIKI_BASE_DOMAIN',
    'dokuwiki.{}'.format(ORCHESTRA_BASE_DOMAIN),
)


SAAS_DOKUWIKI_TEMPLATE_PATH = Setting('SAAS_DOKUWIKI_TEMPLATE_PATH',
    '/var/www/wikifarm/template.tar.gz',
)

SAAS_DOKUWIKI_FARM_PATH = Setting('SAAS_DOKUWIKI_FARM_PATH',
    '/var/www/wikifarm/farm'
)


SAAS_DOKUWIKI_USER = Setting('SAAS_DOKUWIKI_USER',
    'orchestra'
)


SAAS_DOKUWIKI_GROUP = Setting('SAAS_DOKUWIKI_GROUP',
    'orchestra'
)


SAAS_DRUPAL_SITES_PATH = Setting('WEBSITES_DRUPAL_SITES_PATH',
    '/home/httpd/htdocs/drupal-mu/sites/%(site_name)s',
)


SAAS_PHPLIST_DB_USER = Setting('SAAS_PHPLIST_DB_USER',
    'phplist_mu',
    help_text=_("Needed for password changing support."),
)


SAAS_PHPLIST_DB_PASS = Setting('SAAS_PHPLIST_DB_PASS',
    'secret',
    help_text=_("Needed for password changing support."),
)


SAAS_PHPLIST_DB_NAME = Setting('SAAS_PHPLIST_DB_NAME',
    'phplist_mu_%(site_name)s',
    help_text=_("Needed for password changing support."),
)


SAAS_PHPLIST_DB_HOST = Setting('SAAS_PHPLIST_DB_HOST',
    'loclahost',
    help_text=_("Needed for password changing support."),
)


SAAS_PHPLIST_BASE_DOMAIN = Setting('SAAS_PHPLIST_BASE_DOMAIN',
    'lists.{}'.format(ORCHESTRA_BASE_DOMAIN),
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default.",
)


SAAS_PHPLIST_VERIFY_SSL = Setting('SAAS_PHPLIST_VERIFY_SSL',
    True,
    help_text=_("Verify SSL certificate on the HTTP requests performed by the backend."),
)

SAAS_PHPLIST_PATH = Setting('SAAS_PHPLIST_PATH',
    '/var/www/phplist-mu',
    help_text=_("Filesystem path to the phpList source code installed on the server. "
                "Used by <tt>SAAS_PHPLIST_CRONTAB</tt>.")
)

SAAS_PHPLIST_SYSTEMUSER = Setting('SAAS_PHPLIST_SYSTEMUSER',
    'root',
    help_text=_("System user running phpList on the server."
                "Used by <tt>SAAS_PHPLIST_CRONTAB</tt>.")
)

SAAS_PHPLIST_CRONTAB = Setting('SAAS_PHPLIST_CRONTAB',
    ('*/10 * * * * PHPLIST=%(phplist_path)s; export SITE="%(site_name)s"; php $PHPLIST/admin/index.php -c $PHPLIST/config/config.php -p processqueue > /dev/null\n'
     '*/40 * * * * PHPLIST=%(phplist_path)s; export SITE="%(site_name)s"; php $PHPLIST/admin/index.php -c $PHPLIST/config/config.php -p processbounces > /dev/null'),
    help_text=_("<tt>processqueue</tt> and <tt>processbounce</tt> phpList cron execution. "
                "Left blank if you don't want crontab to be configured")
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
