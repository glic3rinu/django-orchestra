import imaplib
import os
import poplib
import smtplib
import time
import textwrap
from email.mime.text import MIMEText

from django.apps import apps
from django.conf import settings as djsettings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse
from selenium.webdriver.support.select import Select

from orchestra.contrib.orchestration.models import Server, Route
from orchestra.contrib.resources.models import Resource
from orchestra.utils.sys import sshrun
from orchestra.utils.tests import BaseLiveServerTestCase, random_ascii, snapshot_on_error, save_response_on_error

from ... import backends, settings
from ...models import Mailbox


class MailboxMixin(object):
    MASTER_SERVER = os.environ.get('ORCHESTRA_SLAVE_SERVER', 'localhost')
    DEPENDENCIES = (
        'orchestra.contrib.orchestration',
        'orchestra.contrib.mails',
        'orchestra.contrib.resources',
    )
    
    def setUp(self):
        super(MailboxMixin, self).setUp()
        self.add_route()
        # clean resource relation from other tests
        apps.get_app_config('resources').reload_relations()
        djsettings.DEBUG = True
    
    def add_route(self):
        server = Server.objects.create(name=self.MASTER_SERVER)
        backend = backends.PasswdVirtualUserBackend.get_name()
        Route.objects.create(backend=backend, match=True, host=server)
        backend = backends.PostfixAddressController.get_name()
        Route.objects.create(backend=backend, match=True, host=server)
    
    def add_quota_resource(self):
        Resource.objects.create(
            name='disk',
            content_type=ContentType.objects.get_for_model(Mailbox),
            period=Resource.LAST,
            verbose_name='Mail quota',
            unit='MB',
            scale=10**6,
            on_demand=False,
            default_allocation=2000
        )
    
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
    
    def login_imap(self, username, password):
        mail = imaplib.IMAP4_SSL(self.MASTER_SERVER)
        status, msg = mail.login(username, password)
        self.assertEqual('OK', status)
        self.assertEqual(['Logged in'], msg)
        return mail
    
    def login_pop3(self, username, password):
        pop = poplib.POP3(self.MASTER_SERVER)
        pop.user(username)
        pop.pass_(password)
        return pop
    
    def send_email(self, to, token):
        msg = MIMEText(token)
        msg['To'] = to
        msg['From'] = 'orchestra@%s' % self.MASTER_SERVER
        msg['Subject'] = 'test'
        server = smtplib.SMTP(self.MASTER_SERVER, 25)
        try:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.sendmail(msg['From'], msg['To'], msg.as_string())
        finally:
            server.quit()
    
    def validate_mailbox(self, username):
        sshrun(self.MASTER_SERVER, "doveadm search -u %s ALL" % username, display=False)
    
    def validate_email(self, username, token):
        home = Mailbox.objects.get(name=username).get_home()
        sshrun(self.MASTER_SERVER, "grep '%s' %s/Maildir/new/*" % (token, home), display=False)
    
    def test_add(self):
        username = '%s_mailbox' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password)
        self.addCleanup(self.delete, username)
        imap = self.login_imap(username, password)
        self.validate_mailbox(username)
    
    def test_change_password(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password)
        self.addCleanup(self.delete, username)
        imap = self.login_imap(username, password)
        new_password = '@!?%spppP001' % random_ascii(5)
        self.change_password(username, new_password)
        imap = self.login_imap(username, new_password)
    
    def test_quota(self):
        username = '%s_mailbox' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add_quota_resource()
        quota = 100
        self.add(username, password, quota=quota)
        self.addCleanup(self.delete, username)
        get_quota = "doveadm quota get -u %s 2>&1|grep STORAGE|awk {'print $5'}" % username
        stdout = sshrun(self.MASTER_SERVER, get_quota, display=False).stdout
        self.assertEqual(quota*1024, int(stdout))
        imap = self.login_imap(username, password)
        imap_quota = int(imap.getquotaroot("INBOX")[1][1][0].split(' ')[-1].split(')')[0])
        self.assertEqual(quota*1024, imap_quota)
    
    def test_send_email(self):
        username = '%s_mailbox' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password)
        self.addCleanup(self.delete, username)
        msg = MIMEText("Hola bishuns")
        msg['To'] = 'noexists@example.com'
        msg['From'] = '%s@%s' % (username, self.MASTER_SERVER)
        msg['Subject'] = "test"
        server = smtplib.SMTP(self.MASTER_SERVER, 25)
        server.login(username, password)
        try:
            server.sendmail(msg['From'], msg['To'], msg.as_string())
        finally:
            server.quit()
    
    def test_address(self):
        username = '%s_mailbox' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password)
        self.addCleanup(self.delete, username)
        domain = '%s_domain.lan' % random_ascii(5)
        name = '%s_name' % random_ascii(5)
        domain = self.account.domains.create(name=domain)
        self.add_address(username, name, domain)
        token = random_ascii(100)
        self.send_email("%s@%s" % (name, domain), token)
        self.validate_email(username, token)
    
    def test_disable(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password)
        self.validate_mailbox(username)
#        self.addCleanup(self.delete, username)
        imap = self.login_imap(username, password)
        self.disable(username)
        self.assertRaises(imap.error, self.login_imap, username, password)
    
    def test_delete(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%sppppP001' % random_ascii(5)
        self.add(username, password)
        imap = self.login_imap(username, password)
        self.validate_mailbox(username)
        mailbox = Mailbox.objects.get(name=username)
        home = mailbox.get_home()
        self.delete(username)
        self.assertRaises(Mailbox.DoesNotExist, Mailbox.objects.get, name=username)
        self.assertRaises(CommandError, self.validate_mailbox, username)
        self.assertRaises(imap.error, self.login_imap, username, password)
        self.assertRaises(CommandError,
                sshrun, self.MASTER_SERVER, 'ls %s' % home, display=False)
    
    def test_delete_address(self):
        username = '%s_mailbox' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password)
        self.addCleanup(self.delete, username)
        domain = '%s_domain.lan' % random_ascii(5)
        name = '%s_name' % random_ascii(5)
        domain = self.account.domains.create(name=domain)
        self.add_address(username, name, domain)
        token = random_ascii(100)
        self.send_email("%s@%s" % (name, domain), token)
        self.validate_email(username, token)
        self.delete_address(username)
        self.send_email("%s@%s" % (name, domain), token)
        self.validate_email(username, token)
    
    def test_custom_filtering(self):
        username = '%s_mailbox' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        folder = random_ascii(5)
        filtering = textwrap.dedent("""
            require "fileinto";
            if true { 
                fileinto "%s";
                stop;
            }""" % folder)
        self.add(username, password, filtering=filtering)
        self.addCleanup(self.delete, username)
        imap = self.login_imap(username, password)
        imap.create(folder)
        self.validate_mailbox(username)
        token = random_ascii(100)
        self.send_email("%s@%s" % (username, settings.MAILBOXES_VIRTUAL_MAILBOX_DEFAULT_DOMAIN), token)
        home = Mailbox.objects.get(name=username).get_home()
        sshrun(self.MASTER_SERVER,
               "grep '%s' %s/Maildir/.%s/new/*" % (token, home, folder), display=False)

# TODO test update shit
# TODO test autoreply


class RESTMailboxMixin(MailboxMixin):
    def setUp(self):
        super(RESTMailboxMixin, self).setUp()
        self.rest_login()
    
    @save_response_on_error
    def add(self, username, password, quota=None, filtering=None):
        extra = {}
        if quota:
            extra.update({
                "resources": [
                    {
                        "name": "disk",
                        "allocated": quota
                    },
                ]
            })
        if filtering:
            extra.update({
                'filtering': 'CUSTOM',
                'custom_filtering': filtering,
            })
        self.rest.mailboxes.create(name=username, password=password, **extra)
    
    @save_response_on_error
    def delete(self, username):
        mailbox = self.rest.mailboxes.retrieve(name=username).get()
        mailbox.delete()
    
    @save_response_on_error
    def change_password(self, username, password):
        mailbox = self.rest.mailboxes.retrieve(name=username).get()
        mailbox.change_password(password)
    
    @save_response_on_error
    def add_address(self, username, name, domain):
        mailbox = self.rest.mailboxes.retrieve(name=username).get()
        domain = self.rest.domains.retrieve(name=domain.name).get()
        self.rest.addresses.create(name=name, domain=domain, mailboxes=[mailbox])
    
    @save_response_on_error
    def delete_address(self, username):
        mailbox = self.rest.mailboxes.retrieve(name=username).get()
        self.rest.addresses.delete()
    
    @save_response_on_error
    def disable(self, username):
        mailbox = self.rest.mailboxes.retrieve(name=username).get()
        mailbox.update(is_active=False)


class AdminMailboxMixin(MailboxMixin):
    def setUp(self):
        super(AdminMailboxMixin, self).setUp()
        self.admin_login()
    
    @snapshot_on_error
    def add(self, username, password, quota=None, filtering=None):
        url = self.live_server_url + reverse('admin:mailboxes_mailbox_add')
        self.selenium.get(url)
        
#        account_input = self.selenium.find_element_by_id('id_account')
#        account_select = Select(account_input)
#        account_select.select_by_value(str(self.account.pk))
        
        name_field = self.selenium.find_element_by_id('id_name')
        name_field.send_keys(username)
        
        password_field = self.selenium.find_element_by_id('id_password1')
        password_field.send_keys(password)
        password_field = self.selenium.find_element_by_id('id_password2')
        password_field.send_keys(password)
        
        if quota is not None:
            quota_id = 'id_resources-resourcedata-content_type-object_id-0-allocated'
            quota_field = self.selenium.find_element_by_id(quota_id)
            quota_field.clear()
            quota_field.send_keys(quota)
        
        if filtering is not None:
            filtering_input = self.selenium.find_element_by_id('id_filtering')
            filtering_select = Select(filtering_input)
            filtering_select.select_by_value("CUSTOM")
            filtering_inline = self.selenium.find_element_by_id('fieldsetcollapser0')
            filtering_inline.click()
            time.sleep(0.5)
            filtering_field = self.selenium.find_element_by_id('id_custom_filtering')
            filtering_field.send_keys(filtering)
        
        name_field.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    @snapshot_on_error
    def delete(self, username):
        mailbox = Mailbox.objects.get(name=username)
        self.admin_delete(mailbox)
    
    @snapshot_on_error
    def change_password(self, username, password):
        mailbox = Mailbox.objects.get(name=username)
        self.admin_change_password(mailbox, password)
    
    @snapshot_on_error
    def add_address(self, username, name, domain):
        url = self.live_server_url + reverse('admin:mailboxes_address_add')
        self.selenium.get(url)
        
        name_field = self.selenium.find_element_by_id('id_name')
        name_field.send_keys(name)
        
        domain_input = self.selenium.find_element_by_id('id_domain')
        domain_select = Select(domain_input)
        domain_select.select_by_value(str(domain.pk))
        
        mailboxes = self.selenium.find_element_by_id('id_mailboxes_add_all_link')
        mailboxes.click()
        time.sleep(0.5)
        name_field.submit()
        
        self.assertNotEqual(url, self.selenium.current_url)
    
    @snapshot_on_error
    def delete_address(self, username):
        mailbox = Mailbox.objects.get(name=username)
        address = mailbox.addresses.get()
        self.admin_delete(address)
    
    @snapshot_on_error
    def disable(self, username):
        mailbox = Mailbox.objects.get(name=username)
        self.admin_disable(mailbox)


class RESTMailboxTest(RESTMailboxMixin, BaseLiveServerTestCase):
    pass


class AdminMailboxTest(AdminMailboxMixin, BaseLiveServerTestCase):
    pass
