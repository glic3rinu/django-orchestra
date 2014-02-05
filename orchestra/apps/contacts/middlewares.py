from threading import local

from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from . import settings
from .models import Contract


@receiver(pre_save)
def pre_save_collector(sender, *args, **kwargs):
    ContractMiddleware.collect('save', sender, *args, **kwargs)

@receiver(pre_delete)
def pre_delete_collector(sender, *args, **kwargs):
    ContractMiddleware.collect('delete', sender, *args, **kwargs)


class ContractMiddleware(object):
    """
    Registers new contracts when non-superusers create objects listed in
    CONTACTS_CONTRACT_MODELS and cancels them when are deleted
    """
    thread_locals = local()
    
    @classmethod
    def get_new_services(cls):
        request = cls.thread_locals.request
        if not hasattr(request, 'new_services'):
            request.new_contracts = set()
        return request.new_contracts
    
    @classmethod
    def get_old_services(cls):
        request = cls.thread_locals.request
        if not hasattr(request, 'old_services'):
            request.old_contracts = set()
        return request.old_contracts
    
    @classmethod
    def collect(cls, action, sender, *args, **kwargs):
        """
        Collects new and deleted service instances in order to create or cancel 
        their contracts on a later time
        """
        request = getattr(cls.thread_locals, 'request', None)
        opts = sender._meta
        model = '%s.%s' % (opts.app_label, opts.object_name)
        if (request is None or
            model != settings.CONTACTS_CONTRACT_MODELS or
            request.user.is_superuser):
                return
        instance = kwargs['instance']
        
        if action == 'save' and instance.pk is None:
            contracts = cls.get_new_services()
            contracts.add(instance)
        elif action == 'delete':
            contracts = cls.get_old_services()
            contracts.add(instance)
    
    def process_request(self, request):
        """ Stores request on a thread local variable """
        type(self).thread_locals.request = request
    
    def process_response(self, request, response):
        """ Creates the new contracts and cancels old ones """
        if hasattr(request, 'user') and not request.user.is_superuser:
            contact = request.user.contact
            for instance in type(self).get_new_services():
                Contract.objects.create(contact=contact, content_object=instance)
            for instance in type(self).get_old_services():
                instance.contract.cancel()
        return response
