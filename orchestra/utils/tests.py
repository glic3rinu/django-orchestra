import datetime
import os
from functools import wraps

from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase, TestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from xvfbwrapper import Xvfb

from orchestra.contrib.accounts.models import Account

from .python import random_ascii


class AppDependencyMixin(object):
    DEPENDENCIES = ()
    
    @classmethod
    def setUpClass(cls):
        current_app = cls.__module__.split('.tests.')[0]
        INSTALLED_APPS = (
            'orchestra',
            'orchestra.contrib.accounts',
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
        # Avoid problems with the overlaping menu when clicking
        settings.ADMIN_TOOLS_MENU = 'admin_tools.menu.Menu'
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
        from orm.api import Api
        super(BaseLiveServerTestCase, self).setUp()
        self.rest = Api(self.live_server_url + '/api/')
        self.rest.enable_logging()
        self.account = self.create_account(superuser=True)
    
    def admin_login(self):
        session = SessionStore()
        session[SESSION_KEY] = self.account_id
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
    
    def take_screenshot(self):
        timestamp = datetime.datetime.now().isoformat().replace(':', '')
        filename = 'screenshot_%s_%s.png' % (self.id(), timestamp)
        path = '/home/orchestra/snapshots'
        self.selenium.save_screenshot(os.path.join(path, filename))
    
    def admin_delete(self, obj):
        opts = obj._meta
        app_label, model_name = opts.app_label, opts.model_name
        delete = reverse('admin:%s_%s_delete' % (app_label, model_name), args=(obj.pk,))
        url = self.live_server_url + delete
        self.selenium.get(url)
        confirmation = self.selenium.find_element_by_name('post')
        confirmation.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    def admin_disable(self, obj):
        opts = obj._meta
        app_label, model_name = opts.app_label, opts.model_name
        change = reverse('admin:%s_%s_change' % (app_label, model_name), args=(obj.pk,))
        url = self.live_server_url + change
        self.selenium.get(url)
        is_active = self.selenium.find_element_by_id('id_is_active')
        is_active.click()
        save = self.selenium.find_element_by_name('_save')
        save.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    def admin_change_password(self, obj, password):
        opts = obj._meta
        app_label, model_name = opts.app_label, opts.model_name
        change_password = reverse('admin:%s_%s_change_password' % (app_label, model_name), args=(obj.pk,))
        url = self.live_server_url + change_password
        self.selenium.get(url)
        
        password_field = self.selenium.find_element_by_id('id_password1')
        password_field.send_keys(password)
        password_field = self.selenium.find_element_by_id('id_password2')
        password_field.send_keys(password)
        password_field.submit()
        
        self.assertNotEqual(url, self.selenium.current_url)

def snapshot_on_error(test):
    @wraps(test)
    def inner(*args, **kwargs):
        try:
            test(*args, **kwargs)
        except:
            self = args[0]
            self.take_screenshot()
            raise
    return inner


def save_response_on_error(test):
    @wraps(test)
    def inner(*args, **kwargs):
        try:
            test(*args, **kwargs)
        except:
            self = args[0]
            timestamp = datetime.datetime.now().isoformat().replace(':', '')
            filename = '%s_%s.html' % (self.id(), timestamp)
            path = '/home/orchestra/snapshots'
            with open(os.path.join(path, filename), 'w') as dumpfile:
                dumpfile.write(self.rest.last_response.content)
            raise
    return inner
