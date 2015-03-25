import json
import re

import requests
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController

from .. import settings


class PhpListSaaSBackend(ServiceController):
    verbose_name = _("phpList SaaS")
    model = 'saas.SaaS'
    default_route_match = "saas.service == 'phplist'"
    block = True
    
    def initialize_database(self, saas, server):
        base_domain = settings.SAAS_PHPLIST_BASE_DOMAIN
        admin_link = 'http://%s/admin/' % saas.get_site_domain()
        admin_content = requests.get(admin_link).content
        if admin_content.startswith('Cannot connect to Database'):
            raise RuntimeError("Database is not yet configured")
        install = re.search(r'([^"]+firstinstall[^"]+)', admin_content)
        if install:
            if not saas.password:
                raise RuntimeError("Password is missing")
            install = install.groups()[0]
            install_link = admin_link + install[1:]
            post = {
                'adminname': saas.name,
                'orgname': saas.account.username,
                'adminemail': saas.account.username,
                'adminpassword': saas.password,
            }
            print json.dumps(post, indent=4)
            response = requests.post(install_link, data=post)
            print response.content
            if response.status_code != 200:
                raise RuntimeError("Bad status code %i" % response.status_code)
        elif saas.password:
            raise NotImplementedError
    
    def save(self, saas):
        self.append(self.initialize_database, saas)
