import ftplib
import re
from functools import partial

import paramiko
from django.conf import settings as djsettings
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse
from selenium.webdriver.support.select import Select

from orchestra.apps.accounts.models import Account
from orchestra.apps.orchestration.models import Server, Route
from orchestra.utils.system import run
from orchestra.utils.tests import BaseLiveServerTestCase, random_ascii

from ... import backends, settings
from ...models import SystemUser


r = partial(run, silent=True, display=False)


class SystemUserMixin(object):
    MASTER_ADDR = 'localhost'
    ACCOUNT_USERNAME = '%s_account' % random_ascii(10)
    DEPENDENCIES = (
        'orchestra.apps.orchestration',
        'orcgestra.apps.systemusers',
    )
    
    def setUp(self):
        super(SystemUserMixin, self).setUp()
        self.add_route()
        djsettings.DEBUG = True
    
    def add_route(self):
        master = Server.objects.create(name=self.MASTER_ADDR)
        backend = backends.SystemUserBackend.get_name()
        Route.objects.create(backend=backend, match=True, host=master)
    
    def save(self):
        raise NotImplementedError
    
    def add(self):
        raise NotImplementedError
    
    def delete(self):
        raise NotImplementedError
    
    def update(self):
        raise NotImplementedError
    
    def disable(self):
        raise NotImplementedError
    
    def add_group(self, username, groupname):
        raise NotImplementedError
    
    def validate_user(self, username):
        idcmd = r("id %s" % username)
        self.assertEqual(0, idcmd.return_code)
        user = SystemUser.objects.get(username=username)
        groups = list(user.groups.values_list('username', flat=True))
        groups.append(user.username)
        idgroups = idcmd.stdout.strip().split(' ')[2]
        idgroups = re.findall(r'\d+\((\w+)\)', idgroups)
        self.assertEqual(set(groups), set(idgroups))
    
    def validate_delete(self, username):
        self.assertRaises(SystemUser.DoesNotExist, SystemUser.objects.get, username=username)
        self.assertRaises(CommandError, run, 'id %s' % username, display=False)
        self.assertRaises(CommandError, run, 'grep "^%s:" /etc/groups' % username, display=False)
        self.assertRaises(CommandError, run, 'grep "^%s:" /etc/passwd' % username, display=False)
        self.assertRaises(CommandError, run, 'grep "^%s:" /etc/shadow' % username, display=False)
    
    def validate_ftp(self, username, password):
        connection = ftplib.FTP(self.MASTER_ADDR)
        connection.login(user=username, passwd=password)
        connection.close()
        
    def validate_sftp(self, username, password):
        transport = paramiko.Transport((self.MASTER_ADDR, 22))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.listdir()
        sftp.close()
    
    def validate_ssh(self, username, password):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.MASTER_ADDR, username=username, password=password)
        transport = ssh.get_transport()
        channel = transport.open_session()
        channel.exec_command('ls')
        self.assertEqual(0, channel.recv_exit_status())
        channel.close()
    
    def test_create_systemuser(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password)
        self.addCleanup(partial(self.delete, username))
        self.validate_user(username)
    
    def test_ftp(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password, shell='/dev/null')
        self.addCleanup(partial(self.delete, username))
        self.assertRaises(paramiko.AuthenticationException, self.validate_sftp, username, password)
        self.assertRaises(paramiko.AuthenticationException, self.validate_ssh, username, password)
    
    def test_sftp(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password, shell='/bin/rssh')
        self.addCleanup(partial(self.delete, username))
        self.validate_sftp(username, password)
        self.assertRaises(AssertionError, self.validate_ssh, username, password)
    
    def test_ssh(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password, shell='/bin/bash')
        self.addCleanup(partial(self.delete, username))
        self.validate_ssh(username, password)
    
    def test_delete_systemuser(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%sppppP001' % random_ascii(5)
        self.add(username, password)
        self.validate_user(username)
        self.delete(username)
        self.validate_delete(username)
    
    def test_add_group_systemuser(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password)
        self.addCleanup(partial(self.delete, username))
        self.validate_user(username)
        username2 = '%s_systemuser' % random_ascii(10)
        password2 = '@!?%spppP001' % random_ascii(5)
        self.add(username2, password2)
        self.addCleanup(partial(self.delete, username2))
        self.validate_user(username2)
        self.add_group(username, username2)
        user = SystemUser.objects.get(username=username)
        groups = list(user.groups.values_list('username', flat=True))
        self.assertIn(username2, groups)
        self.validate_user(username)
    
    def test_disable_systemuser(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password, shell='/dev/null')
        self.addCleanup(partial(self.delete, username))
        self.validate_ftp(username, password)
        self.disable(username)
        self.validate_user(username)
        self.assertRaises(ftplib.error_perm, self.validate_ftp, username, password)


class RESTSystemUserMixin(SystemUserMixin):
    def setUp(self):
        super(RESTSystemUserMixin, self).setUp()
        self.rest_login()
        # create main user
        self.save(self.account.username)
        self.addCleanup(partial(self.delete, self.account.username))
    
    def add(self, username, password, shell='/dev/null'):
        self.rest.systemusers.create(username=username, password=password, shell=shell)
    
    def delete(self, username):
        user = self.rest.systemusers.retrieve(username=username).get()
        user.delete()
    
    def add_group(self, username, groupname):
        user = self.rest.systemusers.retrieve(username=username).get()
        group = self.rest.systemusers.retrieve(username=groupname).get()
        user.groups.append(group) # TODO how to do it with the api?
        user.save()
    
    def disable(self, username):
        user = self.rest.systemusers.retrieve(username=username).get()
        user.is_active = False
        user.save()
    
    def save(self, username):
        user = self.rest.systemusers.retrieve(username=username).get()
        user.save()


class AdminSystemUserMixin(SystemUserMixin):
    def setUp(self):
        super(AdminSystemUserMixin, self).setUp()
        self.admin_login()
        # create main user
        self.save(self.account.username)
        self.addCleanup(partial(self.delete, self.account.username))
    
    def add(self, username, password, shell='/dev/null'):
        url = self.live_server_url + reverse('admin:systemusers_systemuser_add')
        self.selenium.get(url)
        
        username_field = self.selenium.find_element_by_id('id_username')
        username_field.send_keys(username)
        
        password_field = self.selenium.find_element_by_id('id_password1')
        password_field.send_keys(password)
        password_field = self.selenium.find_element_by_id('id_password2')
        password_field.send_keys(password)
        
        account_input = self.selenium.find_element_by_id('id_account')
        account_select = Select(account_input)
        account_select.select_by_value(str(self.account.pk))
        
        shell_input = self.selenium.find_element_by_id('id_shell')
        shell_select = Select(shell_input)
        shell_select.select_by_value(shell)
        
        username_field.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    def delete(self, username):
        user = SystemUser.objects.get(username=username)
        delete = reverse('admin:systemusers_systemuser_delete', args=(user.pk,))
        url = self.live_server_url + delete
        self.selenium.get(url)
        confirmation = self.selenium.find_element_by_name('post')
        confirmation.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    def disable(self, username):
        user = SystemUser.objects.get(username=username)
        change = reverse('admin:systemusers_systemuser_change', args=(user.pk,))
        url = self.live_server_url + change
        self.selenium.get(url)
        is_active = self.selenium.find_element_by_id('id_is_active')
        is_active.click()
        save = self.selenium.find_element_by_name('_save')
        save.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    def add_group(self, username, groupname):
        user = SystemUser.objects.get(username=username)
        change = reverse('admin:systemusers_systemuser_change', args=(user.pk,))
        url = self.live_server_url + change
        self.selenium.get(url)
        groups = self.selenium.find_element_by_id('id_groups_add_all_link')
        groups.click()
        save = self.selenium.find_element_by_name('_save')
        save.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    def save(self, username):
        user = SystemUser.objects.get(username=username)
        change = reverse('admin:systemusers_systemuser_change', args=(user.pk,))
        url = self.live_server_url + change
        self.selenium.get(url)
        save = self.selenium.find_element_by_name('_save')
        save.submit()
        self.assertNotEqual(url, self.selenium.current_url)


class RESTSystemUserTest(RESTSystemUserMixin, BaseLiveServerTestCase):
    pass


class AdminSystemUserTest(AdminSystemUserMixin, BaseLiveServerTestCase):
    def test_create_account(self):
        url = self.live_server_url + reverse('admin:accounts_account_add')
        self.selenium.get(url)
        
        account_username = '%s_account' % random_ascii(10)
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys(account_username)
        
        account_password = '@!?%spppP001' % random_ascii(5)
        password = self.selenium.find_element_by_id('id_password1')
        password.send_keys(account_password)
        password = self.selenium.find_element_by_id('id_password2')
        password.send_keys(account_password)
        
        account_email = 'orchestra@orchestra.lan'
        email = self.selenium.find_element_by_id('id_email')
        email.send_keys(account_email)
        
        contact_short_name = random_ascii(10)
        short_name = self.selenium.find_element_by_id('id_contacts-0-short_name')
        short_name.send_keys(contact_short_name)
        
        email = self.selenium.find_element_by_id('id_contacts-0-email')
        email.send_keys(account_email)
        email.submit()
        
        account = Account.objects.get(username=account_username)
        self.addCleanup(account.delete)
        self.assertNotEqual(url, self.selenium.current_url)
        self.assertEqual(0, r("id %s" % account.username).return_code)
    
    def test_delete_account(self):
        home = self.account.systemusers.get(is_main=True).get_home()
        
        delete = reverse('admin:accounts_account_delete', args=(self.account.pk,))
        url = self.live_server_url + delete
        self.selenium.get(url)
        confirmation = self.selenium.find_element_by_name('post')
        confirmation.submit()
        self.assertNotEqual(url, self.selenium.current_url)
        
        self.assertRaises(CommandError, run, 'ls %s' % home, display=False)
        
        # Recreate a fucking fake account for test cleanup
        self.account = self.create_account(username=self.account.username, superuser=True)
        self.selenium.delete_all_cookies()
        self.admin_login()
