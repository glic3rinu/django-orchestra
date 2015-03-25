import json

import requests
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController

from .. import settings


class GitLabSaaSBackend(ServiceController):
    verbose_name = _("GitLab SaaS")
    model = 'saas.SaaS'
    default_route_match = "saas.service == 'gitlab'"
    block = True
    actions = ('save', 'delete', 'validate_creation')
    
    def get_base_url(self):
        return 'https://%s/api/v3' %  settings.SAAS_GITLAB_DOMAIN
    
    def get_user_url(self, saas):
        user_id = saas.data['user_id']
        return self.get_base_url() + '/users/%i' % user_id
    
    def validate_response(self, response, status_codes):
        if response.status_code not in status_codes:
            raise RuntimeError("[%i] %s" % (response.status_code, response.content))
    
    def authenticate(self):
        login_url = self.get_base_url() + '/session'
        data = {
            'login': 'root',
            'password': settings.SAAS_GITLAB_ROOT_PASSWORD,
        }
        response = requests.post(login_url, data=data)
        self.validate_response(response, [201])
        token = json.loads(response.content)['private_token']
        self.headers = {
            'PRIVATE-TOKEN': token,
        }
    
    def create_user(self, saas, server):
        self.authenticate()
        user_url = self.get_base_url() + '/users'
        data = {
            'email': saas.data['email'],
            'password': saas.password,
            'username': saas.name,
            'name': saas.account.get_full_name(),
        }
        response = requests.post(user_url, data=data, headers=self.headers)
        self.validate_response(response, [201])
        print response.content
        user = json.loads(response.content)
        saas.data['user_id'] = user['id']
        # Using queryset update to avoid triggering backends with the post_save signal
        type(saas).objects.filter(pk=saas.pk).update(data=saas.data)
        print json.dumps(user, indent=4)
    
    def change_password(self, saas, server):
        self.authenticate()
        user_url = self.get_user_url(saas)
        data = {
            'password': saas.password,
        }
        response = requests.patch(user_url, data=data, headers=self.headers)
        self.validate_response(response, [200])
        print json.dumps(json.loads(response.content), indent=4)
    
    def delete_user(self, saas, server):
        self.authenticate()
        user_url = self.get_user_url(saas)
        response = requests.delete(user_url, headers=self.headers)
        self.validate_response(response, [200, 404])
        print json.dumps(json.loads(response.content), indent=4)
    
    def _validate_creation(self, saas, server):
        """ checks if a saas object is valid for creation on the server side """
        self.authenticate()
        username = saas.name
        email = saas.data['email']
        users_url = self.get_base_url() + '/users/'
        users = json.loads(requests.get(users_url, headers=self.headers).content)
        for user in users:
            if user['username'] == username:
                print 'user-exists'
            if user['email'] == email:
                print 'email-exists'
    
    def validate_creation(self, saas):
        self.append(self._validate_creation, saas)
    
    def save(self, saas):
        if hasattr(saas, 'password'):
            if saas.data.get('user_id', None):
                self.append(self.change_password, saas)
            else:
                self.append(self.create_user, saas)
    
    def delete(self, saas):
        self.append(self.delete_user, saas)
