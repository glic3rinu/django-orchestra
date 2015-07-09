import re

import requests
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController

from .. import settings


class PhpListSaaSBackend(ServiceController):
    """
    Creates a new phplist instance on a phpList multisite installation.
    The site is created by means of creating a new database per phpList site, but all sites share the same code.
    
    <tt>// config/config.php
    $site = array_shift((explode(".",$_SERVER['HTTP_HOST'])));
    $database_name = "phplist_mu_{$site}";</tt>
    """
    verbose_name = _("phpList SaaS")
    model = 'saas.SaaS'
    default_route_match = "saas.service == 'phplist'"
    serialize = True
    
    def _save(self, saas, server):
        admin_link = 'https://%s/admin/' % saas.get_site_domain()
        print('admin_link:', admin_link)
        admin_content = requests.get(admin_link, verify=settings.SAAS_PHPLIST_VERIFY_SSL).content.decode('utf8')
        if admin_content.startswith('Cannot connect to Database'):
            raise RuntimeError("Database is not yet configured")
        install = re.search(r'([^"]+firstinstall[^"]+)', admin_content)
        if install:
            if not hasattr(saas, 'password'):
                raise RuntimeError("Password is missing")
            install_path = install.groups()[0]
            install_link = admin_link + install_path[1:]
            post = {
                'adminname': saas.name,
                'orgname': saas.account.username,
                'adminemail': saas.account.username,
                'adminpassword': saas.password,
            }
            response = requests.post(install_link, data=post, verify=settings.SAAS_PHPLIST_VERIFY_SSL)
            print(response.content.decode('utf8'))
            if response.status_code != 200:
                raise RuntimeError("Bad status code %i" % response.status_code)
        else:
            raise NotImplementedError("Change password not implemented")
    
    def save(self, saas):
        if hasattr(saas, 'password'):
            self.append(self._save, saas)
