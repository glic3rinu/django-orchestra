from django.utils.translation import ugettext_lazy as _

from . import AppType
from .. import settings


class WordPressMuApp(AppType):
    name = 'wordpress-mu'
    verbose_name = "WordPress (SaaS)"
    directive = ('fpm', 'fcgi://127.0.0.1:8990/home/httpd/wordpress-mu/')
    help_text = _("This creates a WordPress site on a multi-tenant WordPress server.<br>"
                  "By default this blog is accessible via &lt;app_name&gt;.blogs.orchestra.lan")
    icon = 'orchestra/icons/apps/WordPressMu.png'
    unique_name = True
    option_groups = ()
    fpm_listen = settings.WEBAPPS_WORDPRESSMU_LISTEN


class DokuWikiMuApp(AppType):
    name = 'dokuwiki-mu'
    verbose_name = "DokuWiki (SaaS)"
    directive = ('alias', '/home/httpd/wikifarm/farm/')
    help_text = _("This create a DokuWiki wiki into a shared DokuWiki server.<br>"
                  "By default this wiki is accessible via &lt;app_name&gt;.wikis.orchestra.lan")
    icon = 'orchestra/icons/apps/DokuWikiMu.png'
    unique_name = True
    option_groups = ()
    fpm_listen = settings.WEBAPPS_DOKUWIKIMU_LISTEN


class MoodleMuApp(AppType):
    name = 'moodle-mu'
    verbose_name = "Moodle (SaaS)"
    directive = ('alias', '/home/httpd/wikifarm/farm/')
    help_text = _("This create a Moodle site into a shared Moodle server.<br>"
                  "By default this wiki is accessible via &lt;app_name&gt;.moodle.orchestra.lan")
    icon = 'orchestra/icons/apps/MoodleMu.png'
    unique_name = True
    option_groups = ()
    fpm_listen = settings.WEBAPPS_MOODLEMU_LISTEN


class DrupalMuApp(AppType):
    name = 'drupal-mu'
    verbose_name = "Drupdal (SaaS)"
    directive = ('fpm', 'fcgi://127.0.0.1:8991/home/httpd/drupal-mu/')
    help_text = _("This creates a Drupal site into a multi-tenant Drupal server.<br>"
                  "The installation will be completed after visiting "
                  "http://&lt;app_name&gt;.drupal.orchestra.lan/install.php?profile=standard<br>"
                  "By default this site will be accessible via &lt;app_name&gt;.drupal.orchestra.lan")
    icon = 'orchestra/icons/apps/DrupalMu.png'
    unique_name = True
    option_groups = ()
    fpm_listen = settings.WEBAPPS_DRUPALMU_LISTEN
