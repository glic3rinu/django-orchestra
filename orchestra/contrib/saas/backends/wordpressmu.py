import re

import requests
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController

from . import ApacheTrafficByHost
from .. import settings


class WordpressMuBackend(ServiceController):
    """
    Creates a wordpress site on a WordPress MultiSite installation.
    """
    verbose_name = _("Wordpress multisite")
    model = 'saas.SaaS'
    default_route_match = "saas.service == 'wordpress'"
    doc_settings = (settings,
        ('SAAS_WORDPRESS_ADMIN_PASSWORD', 'SAAS_WORDPRESS_MAIN_URL')
    )
    
    def login(self, session):
        main_url = self.get_main_url()
        login_url = main_url + '/wp-login.php'
        login_data = {
            'log': 'admin',
            'pwd': settings.SAAS_WORDPRESS_ADMIN_PASSWORD,
            'redirect_to': '/wp-admin/'
        }
        response = session.post(login_url, data=login_data)
        if response.url != main_url + '/wp-admin/':
            raise IOError("Failure login to remote application")
    
    def get_main_url(self):
        main_url = settings.SAAS_WORDPRESS_MAIN_URL
        return main_url.rstrip('/')
    
    def validate_response(self, response):
        if response.status_code != 200:
            errors = re.findall(r'<body id="error-page">\n\t<p>(.*)</p></body>', response.content.decode('utf8'))
            raise RuntimeError(errors[0] if errors else 'Unknown %i error' % response.status_code)
    
    def get_id(self, session, saas):
        search = self.get_main_url()
        search += '/wp-admin/network/sites.php?s=%s&action=blogs' % saas.name
        regex = re.compile(
            '<a href="http://[\.\-\w]+/wp-admin/network/site-info\.php\?id=([0-9]+)"\s+'
            'class="edit">%s</a>' % saas.name
        )
        content = session.get(search).content.decode('utf8')
        # Get id
        ids = regex.search(content)
        if not ids:
            raise RuntimeError("Blog '%s' not found" % saas.name)
        ids = ids.groups()
        if len(ids) > 1:
            raise ValueError("Multiple matches")
        # Get wpnonce
        wpnonce = re.search(r'<span class="delete">(.*)</span>', content).groups()[0]
        wpnonce = re.search(r'_wpnonce=([^"]*)"', wpnonce).groups()[0]
        return int(ids[0]), wpnonce
    
    def create_blog(self, saas, server):
        session = requests.Session()
        self.login(session)
        
        # Check if blog already exists
        try:
            self.get_id(session, saas)
        except RuntimeError:
            url = self.get_main_url()
            url += '/wp-admin/network/site-new.php'
            content = session.get(url).content.decode('utf8')
            
            wpnonce = re.compile('name="_wpnonce_add-blog"\s+value="([^"]*)"')
            wpnonce = wpnonce.search(content).groups()[0]
            
            url += '?action=add-site'
            data = {
                'blog[domain]': saas.name,
                'blog[title]': saas.name,
                'blog[email]': saas.account.email,
                '_wpnonce_add-blog': wpnonce,
            }
            
            # Validate response
            response = session.post(url, data=data)
            self.validate_response(response)
    
    def delete_blog(self, saas, server):
        session = requests.Session()
        self.login(session)
        
        try:
            id, wpnonce = self.get_id(session, saas)
        except RuntimeError:
            pass
        else:
            delete = self.get_main_url()
            delete += '/wp-admin/network/sites.php?action=confirm&action2=deleteblog'
            delete += '&id=%d&_wpnonce=%s' % (id, wpnonce)
            
            content = session.get(delete).content.decode('utf8')
            wpnonce = re.compile('name="_wpnonce"\s+value="([^"]*)"')
            wpnonce = wpnonce.search(content).groups()[0]
            data = {
                'action': 'deleteblog',
                'id': id,
                '_wpnonce': wpnonce,
                '_wp_http_referer': '/wp-admin/network/sites.php',
            }
            delete = self.get_main_url()
            delete += '/wp-admin/network/sites.php?action=deleteblog'
            response = session.post(delete, data=data)
            self.validate_response(response)
    
    def save(self, saas):
        self.append(self.create_blog, saas)
    
    def delete(self, saas):
        self.append(self.delete_blog, saas)


class WordpressMuTraffic(ApacheTrafficByHost):
    __doc__ = ApacheTrafficByHost.__doc__
    verbose_name = _("Wordpress MU Traffic")
    default_route_match = "saas.service == 'wordpress'"
    doc_settings = (settings,
        ('SAAS_TRAFFIC_IGNORE_HOSTS', 'SAAS_WORDPRESS_LOG_PATH')
    )
    log_path = settings.SAAS_WORDPRESS_LOG_PATH
