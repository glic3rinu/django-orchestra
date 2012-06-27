from django.utils import unittest
from contacts.models import Contact, Contract, CancelationPeriod
from dns.models import Domain, Subdomain
from django.contrib.auth.models import User
from web.models import SystemUser, SystemGroup, VirtualHost
from datetime import datetime

class CancelationTestCase(unittest.TestCase):
    def setUp(self):
        self.main_contact = Contact.objects.create(name='main_contact')
        self.domain_1 = Domain.objects.create(name='domain_1', extension='ORG')
        self.contract_domain_1 = Contract.objects.create(content_object=self.domain_1, contact=self.main_contact)
        self.subdomain_1 = Subdomain.objects.create(domain=self.domain_1, name='subdomain_1')
        self.contract_subdomain_1 = Contract.objects.create(content_object=self.subdomain_1, contact=self.main_contact)
        self.subdomain_2 = Subdomain.objects.create(domain=self.domain_1, name='subdomain_2')
        self.contract_subdomain_2 = Contract.objects.create(content_object=self.subdomain_2, contact=self.main_contact)
        self.user_1 = User.objects.create(username='user_1')
        self.contract_user_1 = Contract.objects.create(content_object=self.user_1, contact=self.main_contact)
        self.system_group = SystemGroup.objects.create(name='group_1', gid='1001')
        self.contract_system_group = Contract.objects.create(content_object=self.system_group, contact=self.main_contact)
        self.system_user_1 = SystemUser.objects.create(user=self.user_1, uid='1001', primary_group=self.system_group)
        self.contract_system_user = Contract.objects.create(content_object=self.system_user_1, contact=self.main_contact)
        self.virtual_host_1 = VirtualHost.objects.create(user=self.system_user)
        self.virtual_host_1.domains = [self.domain_1, self.subdomain_1]
        self.virtual_host_1.save()
        self.contract_virtual_host_1 = Contract.objects.create(content_object=self.virtual_host_1, contact=self.main_contact)


        
    def test(self):
        self.date_1 = datetime.now()
        self.contract_domain_1.schedule_cancelation(date=self.date_1)
        
        self.assertEqual(self.contract_domain.cancel_date, self.date_1)
        self.assertEqual(self.contract_subdomain_1.cancel_date, self.date_1)
        self.assertEqual(self.contract_subdomain_2.cancel_date, self.date_1)
        self.assertEqual(self.virtual_host_1.cancel_date, self.date_1)
        
