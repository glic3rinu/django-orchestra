import ftplib
import os
import re
import time
from functools import partial

import paramiko
from django.conf import settings as djsettings
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse
from selenium.webdriver.support.select import Select

from orchestra.admin.utils import change_url
from orchestra.contrib.accounts.models import Account
from orchestra.contrib.orchestration.models import Server, Route
from orchestra.utils.sys import run, sshrun
from orchestra.utils.tests import (BaseLiveServerTestCase, random_ascii, snapshot_on_error,
        save_response_on_error)

from ... import backends
from ...models import SystemUser


r = partial(run, silent=True, display=False)
sshr = partial(sshrun, silent=True, display=False)


class SystemUserMixin(object):
    MASTER_SERVER = os.environ.get('ORCHESTRA_MASTER_SERVER', 'localhost')
    DEPENDENCIES = (
        'orchestra.contrib.orchestration',
        'orcgestra.apps.systemusers',
    )
    
    def setUp(self):
        super(SystemUserMixin, self).setUp()
        self.add_route()
        djsettings.DEBUG = True
    
    def add_route(self):
        master = Server.objects.create(name=self.MASTER_SERVER)
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
        idcmd = sshr(self.MASTER_SERVER, "id %s" % username)
        self.assertEqual(0, idcmd.exit_code)
        user = SystemUser.objects.get(username=username)
        groups = list(user.groups.values_list('username', flat=True))
        groups.append(user.username)
        idgroups = idcmd.stdout.strip().split(' ')[2]
        idgroups = re.findall(r'\d+\((\w+)\)', idgroups)
        self.assertEqual(set(groups), set(idgroups))
    
    def validate_delete(self, username):
        self.assertRaises(SystemUser.DoesNotExist, SystemUser.objects.get, username=username)
        self.assertRaises(CommandError,
                sshrun, self.MASTER_SERVER, 'id %s' % username, display=False)
        self.assertRaises(CommandError,
                sshrun, self.MASTER_SERVER, 'grep "^%s:" /etc/groups' % username, display=False)
        self.assertRaises(CommandError,
                sshrun, self.MASTER_SERVER, 'grep "^%s:" /etc/passwd' % username, display=False)
        self.assertRaises(CommandError,
                sshrun, self.MASTER_SERVER, 'grep "^%s:" /etc/shadow' % username, display=False)
        # Home will be deleted on account delete, see test_delete_account
    
    def validate_ftp(self, username, password):
        ftp = ftplib.FTP(self.MASTER_SERVER)
        ftp.login(user=username, passwd=password)
        ftp.close()
        
    def validate_sftp(self, username, password):
        transport = paramiko.Transport((self.MASTER_SERVER, 22))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.listdir()
        sftp.close()
    
    def validate_ssh(self, username, password):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.MASTER_SERVER, username=username, password=password)
        transport = ssh.get_transport()
        channel = transport.open_session()
        channel.exec_command('ls')
        self.assertEqual(0, channel.recv_exit_status())
        channel.close()
    
    def test_add(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password)
        self.addCleanup(self.delete, username)
        self.validate_user(username)
    
    def test_ftp(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password, shell='/dev/null')
        self.addCleanup(self.delete, username)
        self.assertRaises(paramiko.AuthenticationException,
                self.validate_sftp, username, password)
        self.assertRaises(paramiko.AuthenticationException,
                self.validate_ssh, username, password)
    
    def test_sftp(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password, shell='/bin/rssh')
        self.addCleanup(self.delete, username)
        self.validate_sftp(username, password)
        self.assertRaises(AssertionError, self.validate_ssh, username, password)
    
    def test_ssh(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password, shell='/bin/bash')
        self.addCleanup(self.delete, username)
        self.validate_ssh(username, password)
    
    def test_delete(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%sppppP001' % random_ascii(5)
        self.add(username, password)
        self.validate_user(username)
        self.delete(username)
        self.validate_delete(username)
        self.assertRaises(Exception, self.delete, self.account.username)
    
    def test_add_group(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password)
        self.addCleanup(self.delete, username)
        self.validate_user(username)
        username2 = '%s_systemuser' % random_ascii(10)
        password2 = '@!?%spppP001' % random_ascii(5)
        self.add(username2, password2)
        self.addCleanup(self.delete, username2)
        self.validate_user(username2)
        self.add_group(username, username2)
        user = SystemUser.objects.get(username=username)
        groups = list(user.groups.values_list('username', flat=True))
        self.assertIn(username2, groups)
        self.validate_user(username)
    
    def test_disable(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password, shell='/dev/null')
        self.addCleanup(self.delete, username)
        self.validate_ftp(username, password)
        self.disable(username)
        self.validate_user(username)
        self.assertRaises(ftplib.error_perm, self.validate_ftp, username, password)
    
    def test_change_password(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password)
        self.addCleanup(self.delete, username)
        self.validate_ftp(username, password)
        new_password = '@!?%spppP001' % random_ascii(5)
        self.change_password(username, new_password)
        self.validate_ftp(username, new_password)

# TODO test resources


class RESTSystemUserMixin(SystemUserMixin):
    def setUp(self):
        super(RESTSystemUserMixin, self).setUp()
        self.rest_login()
        # create main user
        self.save(self.account.username)
        self.addCleanup(self.delete_account, self.account.username)
    
    @save_response_on_error
    def add(self, username, password, shell='/dev/null'):
        self.rest.systemusers.create(username=username, password=password, shell=shell)
    
    @save_response_on_error
    def delete(self, username):
        user = self.rest.systemusers.retrieve(username=username).get()
        user.delete()
    
    @save_response_on_error
    def add_group(self, username, groupname):
        user = self.rest.systemusers.retrieve(username=username).get()
        user.groups.append({'username': groupname})
        user.save()
    
    @save_response_on_error
    def disable(self, username):
        user = self.rest.systemusers.retrieve(username=username).get()
        user.is_active = False
        user.save()
    
    @save_response_on_error
    def save(self, username):
        user = self.rest.systemusers.retrieve(username=username).get()
        user.save()
    
    @save_response_on_error
    def change_password(self, username, password):
        user = self.rest.systemusers.retrieve(username=username).get()
        user.set_password(password)
    
    def delete_account(self, username):
        self.rest.account.delete()


class AdminSystemUserMixin(SystemUserMixin):
    def setUp(self):
        super(AdminSystemUserMixin, self).setUp()
        self.admin_login()
        # create main user
        self.save(self.account.username)
        self.addCleanup(self.delete_account, self.account.username)
    
    @snapshot_on_error
    def add(self, username, password, shell='/dev/null'):
        url = self.live_server_url + reverse('admin:systemusers_systemuser_add')
        self.selenium.get(url)
        
        username_field = self.selenium.find_element_by_id('id_username')
        username_field.send_keys(username)
        
        password_field = self.selenium.find_element_by_id('id_password1')
        password_field.send_keys(password)
        password_field = self.selenium.find_element_by_id('id_password2')
        password_field.send_keys(password)
        
        shell_input = self.selenium.find_element_by_id('id_shell')
        shell_select = Select(shell_input)
        shell_select.select_by_value(shell)
        
        username_field.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    @snapshot_on_error
    def delete(self, username):
        user = SystemUser.objects.get(username=username)
        self.admin_delete(user)
    
    @snapshot_on_error
    def delete_account(self, username):
        account = Account.objects.get(username=username)
        self.admin_delete(account)
    
    @snapshot_on_error
    def disable(self, username):
        user = SystemUser.objects.get(username=username)
        self.admin_disable(user)
    
    @snapshot_on_error
    def add_group(self, username, groupname):
        user = SystemUser.objects.get(username=username)
        url = self.live_server_url + change_url(user)
        self.selenium.get(url)
        groups = self.selenium.find_element_by_id('id_groups_add_all_link')
        groups.click()
        time.sleep(0.5)
        save = self.selenium.find_element_by_name('_save')
        save.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    @snapshot_on_error
    def save(self, username):
        user = SystemUser.objects.get(username=username)
        url = self.live_server_url + change_url(user)
        self.selenium.get(url)
        save = self.selenium.find_element_by_name('_save')
        save.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    @snapshot_on_error
    def change_password(self, username, password):
        user = SystemUser.objects.get(username=username)
        self.admin_change_password(user, password)


class RESTSystemUserTest(RESTSystemUserMixin, BaseLiveServerTestCase):
    pass


class AdminSystemUserTest(AdminSystemUserMixin, BaseLiveServerTestCase):
    @snapshot_on_error
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
        
        full_name = random_ascii(10)
        full_name_field = self.selenium.find_element_by_id('id_full_name')
        full_name_field.send_keys(full_name)
        
        account_email = 'orchestra@orchestra.lan'
        email = self.selenium.find_element_by_id('id_email')
        email.send_keys(account_email)
        
        contact_short_name = random_ascii(10)
        short_name = self.selenium.find_element_by_id('id_contacts-0-short_name')
        short_name.send_keys(contact_short_name)
        
        email = self.selenium.find_element_by_id('id_contacts-0-email')
        email.send_keys(account_email)
        email.submit()
        self.assertNotEqual(url, self.selenium.current_url)
        
        self.addCleanup(self.delete_account, account_username)
        self.assertEqual(0, sshr(self.MASTER_SERVER, "id %s" % account_username).exit_code)
    
    @snapshot_on_error
    def test_delete_account(self):
        home = self.account.main_systemuser.get_home()
        self.admin_delete(self.account)
        self.assertRaises(CommandError, run, 'ls %s' % home, display=False)
        # Recreate a fucking fake account for test cleanup
        self.account = self.create_account(username=self.account.username, superuser=True)
        self.selenium.delete_all_cookies()
        self.admin_login()
    
    @snapshot_on_error
    def test_disable_account(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password)
        self.addCleanup(self.delete, username)
        self.validate_ftp(username, password)
        self.disable(username)
        self.validate_user(username)
        
        disable = reverse('admin:accounts_account_disable', args=(self.account.pk,))
        url = self.live_server_url + disable
        self.selenium.get(url)
        confirmation = self.selenium.find_element_by_name('post')
        confirmation.submit()
        self.assertNotEqual(url, self.selenium.current_url)
        
        self.assertRaises(ftplib.error_perm, self.validate_ftp, username, password)
        self.selenium.get(url)
        self.assertNotEqual(url, self.selenium.current_url)
        
        # Reenable for test cleanup
        self.account.is_active = True
        self.account.save()
        self.admin_login()
