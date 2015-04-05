import re

import requests
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController


class PhpListSaaSBackend(ServiceController):
    verbose_name = _("phpList SaaS")
    model = 'saas.SaaS'
    default_route_match = "saas.service == 'phplist'"
    block = True
    
    def _save(self, saas, server):
        admin_link = 'http://%s/admin/' % saas.get_site_domain()
        admin_content = requests.get(admin_link).content
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
            response = requests.post(install_link, data=post)
            print(response.content)
            if response.status_code != 200:
                raise RuntimeError("Bad status code %i" % response.status_code)
        else:
            raise NotImplementedError("Change password not implemented")
    
    def save(self, saas):
        if hasattr(saas, 'password'):
            self.append(self._save, saas)
