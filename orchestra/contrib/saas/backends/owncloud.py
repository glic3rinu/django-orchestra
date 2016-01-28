import re
import sys
import textwrap
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import requests
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController

from . import ApacheTrafficByHost
from .. import settings


class OwnCloudBackend(ServiceController):
    """
    Creates a wordpress site on a WordPress MultiSite installation.
    
    You should point it to the database server
    """
    verbose_name = _("ownCloud SaaS")
    model = 'saas.SaaS'
    default_route_match = "saas.service == 'owncloud'"
    doc_settings = (settings,
        ('SAAS_OWNCLOUD_API_URL',)
    )
    
    def validate_response(self, response):
        if response.status_code != requests.codes.ok:
            request = response.request
            context = (request.method, response.url, request.body, response.status_code)
            raise RuntimeError("%s %s '%s' HTTP %s" % context)
        root = ET.fromstring(response.text)
        statuscode = root.find("./meta/statuscode").text
        if statuscode != '100':
            message = root.find("./meta/status").text
            request = response.request
            context = (request.method, response.url, request.body, statuscode, message)
            raise RuntimeError("%s %s '%s' ERROR %s, %s" % context)
    
    def api_call(self, action, url_path, *args, **kwargs):
        BASE_URL = settings.SAAS_OWNCLOUD_API_URL.rstrip('/')
        url = '/'.join((BASE_URL, url_path))
        response = action(url, *args, **kwargs)
        self.validate_response(response)
        return response
    
    def api_get(self, url_path, *args, **kwargs):
        return self.api_call(requests.get, url_path, *args, **kwargs)
    
    def api_post(self, url_path, *args, **kwargs):
        return self.api_call(requests.post, url_path, *args, **kwargs)
    
    def api_put(self, url_path, *args, **kwargs):
        return self.api_call(requests.put, url_path, *args, **kwargs)
    
    def api_delete(self, url_path, *args, **kwargs):
        return self.api_call(requests.delete, url_path, *args, **kwargs)
    
    def create(self, saas):
        data = {
            'userid': saas.name,
            'password': saas.password
        }
        self.api_post('users', data)
    
    def update(self, saas):
        data = {
            'password': saas.password,
        }
        self.api_put('users/%s' % saas.name, data)
    
    def update_or_create(self, saas, server):
        try:
            self.api_get('users/%s' % saas.name)
        except RuntimeError:
            if getattr(saas, 'password'):
                self.create(saas)
            else:
                raise
        else:
            if getattr(saas, 'password'):
                self.update(saas)
    
    def remove(self, saas, server):
        self.api_delete('users/%s' % saas.name)
    
    def save(self, saas):
        self.append(self.update_or_create, saas)
    
    def delete(self, saas):
        self.append(self.remove, saas)


class OwncloudTraffic(ApacheTrafficByHost):
    __doc__ = ApacheTrafficByHost.__doc__
    verbose_name = _("ownCloud SaaS Traffic")
    default_route_match = "saas.service == 'owncloud'"
    doc_settings = (settings,
        ('SAAS_TRAFFIC_IGNORE_HOSTS', 'SAAS_OWNCLOUD_LOG_PATH')
    )
    log_path = settings.SAAS_OWNCLOUD_LOG_PATH
