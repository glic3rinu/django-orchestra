import re

import requests
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController

from . import SaaSServiceMixin
from .. import settings


class WordpressMuBackend(SaaSServiceMixin, ServiceController):
    verbose_name = _("Wordpress multisite")
    
    @property
    def script(self):
        return self.cmds
    
    def login(self, session):
        base_url = self.get_base_url()
        login_url = base_url + '/wp-login.php'
        login_data = {
            'log': 'admin',
            'pwd': settings.WEBAPPS_WORDPRESSMU_ADMIN_PASSWORD,
            'redirect_to': '/wp-admin/'
        }
        response = session.post(login_url, data=login_data)
        if response.url != base_url + '/wp-admin/':
            raise IOError("Failure login to remote application")
    
    def get_base_url(self):
        base_url = settings.WEBAPPS_WORDPRESSMU_BASE_URL
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        return base_url
    
    def create_blog(self, webapp, server):
        emails = webapp.account.contacts.filter(email_usage__contains='')
        email = emails.values_list('email', flat=True).first()
        
        base_url = self.get_base_url()
        session = requests.Session()
        self.login(session)
        
        url = base_url + '/wp-admin/network/site-new.php'
        content = session.get(url).content
        wpnonce = re.compile('name="_wpnonce_add-blog"\s+value="([^"]*)"')
        wpnonce = wpnonce.search(content).groups()[0]
        
        url += '?action=add-site'
        data = {
            'blog[domain]': webapp.name,
            'blog[title]': webapp.name,
            'blog[email]': email,
            '_wpnonce_add-blog': wpnonce,
        }
        # TODO validate response
        response = session.post(url, data=data)
    
    def delete_blog(self, webapp, server):
        # OH, I've enjoied so much coding this methods that I want to thanks
        # the wordpress team for the excellent software they are producing
        context = self.get_context(webapp)
        session = requests.Session()
        self.login(session)
        
        base_url = self.get_base_url()
        search = base_url + '/wp-admin/network/sites.php?s=%(name)s&action=blogs' % context
        regex = re.compile(
            '<a href="http://[\.\-\w]+/wp-admin/network/site-info\.php\?id=([0-9]+)"\s+'
            'class="edit">%(name)s</a>' % context
        )
        content = session.get(search).content
        ids = regex.search(content).groups()
        if len(ids) > 1:
            raise ValueError("Multiple matches")
        
        delete = re.compile('<span class="delete">(.*)</span>')
        content = delete.search(content).groups()[0]
        wpnonce = re.compile('_wpnonce=([^"]*)"')
        wpnonce = wpnonce.search(content).groups()[0]
        delete = '/wp-admin/network/sites.php?action=confirm&action2=deleteblog'
        delete += '&id=%d&_wpnonce=%d' % (ids[0], wpnonce)
        
        content = session.get(delete).content
        wpnonce = re.compile('name="_wpnonce"\s+value="([^"]*)"')
        wpnonce = wpnonce.search(content).groups()[0]
        data = {
            'action': 'deleteblog',
            'id': ids[0],
            '_wpnonce': wpnonce,
            '_wp_http_referer': '/wp-admin/network/sites.php',
        }
        delete = base_url + '/wp-admin/network/sites.php?action=deleteblog'
        session.post(delete, data=data)
    
    def save(self, webapp):
        self.append(self.create_blog, webapp)
    
    def delete(self, webapp):
        self.append(self.delete_blog, webapp)
