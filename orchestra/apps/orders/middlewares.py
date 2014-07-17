from threading import local

from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.http.response import HttpResponseServerError

from orchestra.core import services
from orchestra.utils.python import OrderedSet

from .models import Order


@receiver(pre_save, dispatch_uid='orders.ppre_save_collector')
def pre_save_collector(sender, *args, **kwargs):
    if sender in services:
        OrderMiddleware.collect(Order.SAVE, **kwargs)

@receiver(pre_delete, dispatch_uid='orders.pre_delete_collector')
def pre_delete_collector(sender, *args, **kwargs):
    if sender in services:
        OrderMiddleware.collect(Order.DELETE, **kwargs)


class OrderCandidate(object):
    def __unicode__(self):
        return "{}.{}()".format(str(self.instance), self.action)
    
    def __init__(self, instance, action):
        self.instance = instance
        self.action = action
    
    def __hash__(self):
        """ set() """
        opts = self.instance._meta
        model = opts.app_label + opts.model_name
        return hash(model + str(self.instance.pk) + self.action)
    
    def __eq__(self, candidate):
        """ set() """
        return hash(self) == hash(candidate)


class OrderMiddleware(object):
    """
    Stores all the operations derived from save and delete signals and executes them
    at the end of the request/response cycle
    """
    # Thread local is used because request object is not available on model signals
    thread_locals = local()
    
    @classmethod
    def get_order_candidates(cls):
        # Check if an error poped up before OrdersMiddleware.process_request()
        if hasattr(cls.thread_locals, 'request'):
            request = cls.thread_locals.request
            if not hasattr(request, 'order_candidates'):
                request.order_candidates = OrderedSet()
            return request.order_candidates
        return set()
    
    @classmethod
    def collect(cls, action, **kwargs):
        """ Collects all pending operations derived from model signals """
        request = getattr(cls.thread_locals, 'request', None)
        if request is None:
            return
        order_candidates = cls.get_order_candidates()
        instance = kwargs['instance']
        order_candidates.add(OrderCandidate(instance, action))
    
    def process_request(self, request):
        """ Store request on a thread local variable """
        type(self).thread_locals.request = request
    
    def process_response(self, request, response):
        if not isinstance(response, HttpResponseServerError):
            candidates = type(self).get_order_candidates()
            Order.process_candidates(candidates)
        return response
