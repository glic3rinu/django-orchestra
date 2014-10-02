import string
import random

from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.test import LiveServerTestCase, TestCase
from orm.api import Api
from selenium.webdriver.firefox.webdriver import WebDriver
from xvfbwrapper import Xvfb

from orchestra.apps.accounts.models import Account


def random_ascii(length):
    return ''.join([random.choice(string.hexdigits) for i in range(0, length)]).lower()


class AppDependencyMixin(object):
    DEPENDENCIES = ()
    
    @classmethod
    def setUpClass(cls):
        current_app = cls.__module__.split('.tests.')[0]
        INSTALLED_APPS = (
            'orchestra',
            'orchestra.apps.accounts',
            current_app
        )
        INSTALLED_APPS += cls.DEPENDENCIES
        INSTALLED_APPS += (
            # Third-party apps
            'south',
            'django_extensions',
            'djcelery',
            'djcelery_email',
            'fluent_dashboard',
            'admin_tools',
            'admin_tools.theming',
            'admin_tools.menu',
            'admin_tools.dashboard',
            'rest_framework',
            # Django.contrib
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.admin',
        )
        settings.INSTALLED_APPS = INSTALLED_APPS
        super(AppDependencyMixin, cls).setUpClass()


class BaseTestCase(TestCase, AppDependencyMixin):
    def create_account(self, username='', superuser=False):
        if not username:
            username = '%s_superaccount' % random_ascii(5)
        password = 'orchestra'
        if superuser:
            return Account.objects.create_superuser(username, password=password, email='orchestra@orchestra.org')
        return Account.objects.create_user(username, password=password, email='orchestra@orchestra.org')


class BaseLiveServerTestCase(AppDependencyMixin, LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.vdisplay = Xvfb()
        cls.vdisplay.start()
        cls.selenium = WebDriver()
        super(BaseLiveServerTestCase, cls).setUpClass()
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        cls.vdisplay.stop()
        super(BaseLiveServerTestCase, cls).tearDownClass()
    
    def create_account(self, username='', superuser=False):
        if not username:
            username = '%s_superaccount' % random_ascii(5)
        password = 'orchestra'
        self.account_password = password
        if superuser:
            return Account.objects.create_superuser(username, password=password, email='orchestra@orchestra.org')
        return Account.objects.create_user(username, password=password, email='orchestra@orchestra.org')
    
    def setUp(self):
        super(BaseLiveServerTestCase, self).setUp()
        self.rest = Api(self.live_server_url + '/api/')
        self.account = self.create_account(superuser=True)
    
    def admin_login(self):
        session = SessionStore()
        session[SESSION_KEY] = self.account.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()
        ## to set a cookie we need to first visit the domain.
        self.selenium.get(self.live_server_url + '/admin/')
        self.selenium.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key, #
            path='/',
        ))
    
    def rest_login(self):
        self.rest.login(username=self.account.username, password=self.account_password)
