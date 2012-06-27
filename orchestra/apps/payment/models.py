from django.db import models
from django.utils.translation import ugettext as _
from billing.models import Bill, bill_pre_send
from contacts.models import Contact
from django import template as Template
from django.db.models import Q
from django.dispatch import receiver
from djangoplugins.fields import PluginField
from payment import settings
from plugins import PaymentMethod


#TODO: this should go on form choices in order to make it dinamic under disable/activation
PAYMENT_METHODS = []
#for plugin in PaymentMethod.get_plugins():
#    if plugin.is_active:    
#        PAYMENT_METHODS.append((plugin.name, _(plugin.title)))


class PaymentDetails(models.Model):
    ALL = 'all'
    CHARGE = 'charge'
    REFOUND = 'refound'
    OPERATION_CHOICES = ((ALL, _('All')),
                         (CHARGE, _('Charge')),
                         (REFOUND, _('Refound')),)

    contact = models.ForeignKey('contacts.Contact')
    priority = models.IntegerField(null=True, blank=True)
#    method = models.CharField(max_length=32, choices=PAYMENT_METHODS, default=settings.DEFAULT_PAYMENT_METHOD)
    method = PluginField(PaymentMethod)
    data = models.CharField(max_length=255)
    filter = models.CharField(max_length=64, choices=settings.METHOD_FILTER_CHOICES, default=settings.DEFAULT_METHOD_FILTER)
    operation = models.CharField(max_length=16, choices=OPERATION_CHOICES, default=settings.DEFAULT_OPERATION)

    class Meta:
        unique_together = ('contact', 'priority', 'method', 'operation')

    def __unicode__(self):
        return "%s:%s" % (self.contact.pk, self.method.name)

    @property
    def expression(self):
        #TODO method.get_expression
        return eval("settings.%s_EXPRESSION" % self.filter.upper())


    @property
    def interpreted_data(self):
        #exec "from payment.gateways.%s.interpreter import PaymentDetail as interpreter" % (self.method)
        return self.method.get_plugin().payment_details_interpreter(self)
#        return interpreter(self)


    @classmethod
    def get_buyer_details(cls, bill, total):
        if total > 0: operation = cls.CHARGE
        else: operation = cls.REFOUND
        for detail in cls.objects.filter(Q(contact=bill.buyer) & Q(Q(operation=operation) | Q(operation=cls.ALL))).order_by('priority'):
            if eval(detail.expression):
                return detail
        raise KeyError
        

    @classmethod
    def get_seller_details(cls, bill, method):
        for detail in cls.objects.filter(contact=bill.seller, method=method).order_by('priority'):
            if eval(detail.expression):
                return detail
        raise KeyError

    @classmethod
    def render_bill_payment_comment(cls, bill):
        self = cls.get_buyer_details(bill, bill.total)
        template_name = "%s_bill_payment_comment.html" % self.method.name
        template = Template.loader.get_template(template_name)
        return template.render(Template.Context({'interpreted_details': self.interpreted_data, 'bill': bill}))
        

class Transaction(models.Model):
    """ Represents a single transaction related to their bill """
    #group_id = models.CharField(max_length=32, blank=True)
    #method = models.CharField(max_length=5, choices=PAYMENT_METHODS, default=settings.DEFAULT_PAYMENT_METHOD)
    #TODO: This shit breaks syncdb
    method = PluginField(PaymentMethod)
    status = models.CharField(max_length=32, choices=settings.PAYMENT_STATUS_CHOICES, default=settings.DEFAULT_INITIAL_STATUS)
    data = models.TextField( blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default=settings.DEFAULT_CURRENCY)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    bill = models.ForeignKey('billing.bill')
    dependency = models.ForeignKey('self', null=True, blank=True)

    def __unicode__(self):
        return str(self.pk)

    def save(self, *args, **kwargs):
        super(Transaction, self).save(*args, **kwargs)
        if self.pk and (self.status == settings.CONFIRMED or self.status == settings.REJECTED):
            for related in Transaction.objects.filter(dependency=self):
                related.unlock()
    
    def get_method(self):
        return PaymentDetails.get_buyer_details(self.bill, self.total).method
    
    def unlock(self):
        if self.dependency.status == settings.CONFIRMED:
            self.total = self.dependency.total - self.total
        self.method = self.get_method()
        self.dependency = None
        if self.total == 0: self.status = settings.CONFIRMED
        else: self.status = self.method.get_plugin().initial_state
        self.save()
        
    @classmethod
    def create(cls, bill):

        transaction = Transaction(bill=bill)
        buyer_payment_detail = PaymentDetails.get_buyer_details(bill, bill.total)
        dependencies = Transaction.objects.filter(bill=bill).exclude(status=settings.CONFIRMED).exclude(status=settings.REJECTED).order_by('created')
        if dependencies:
            transaction.status = settings.LOCKED
            transaction.dependency = dependencies[0]
            transaction.total = bill.total
        else:
            method = buyer_payment_detail.method
            seller_payment_detail = PaymentDetails.get_seller_details(bill, method)
            transaction.method = method
            transaction.total = str(bill.total)
            if float(transaction.total) == 0.00: 
                transaction.status = settings.DISCARTED
            else: 
                transaction.status = method.get_plugin().initial_state
            transaction.save()
            print dir(buyer_payment_detail.interpreted_data)
            transaction.data = method.get_plugin().get_transaction_data(buyer_payment_detail.interpreted_data, 
                                                                        seller_payment_detail.interpreted_data, 
                                                                        bill, 
                                                                        transaction.pk)
        transaction.save()
        return transaction

    @property
    def interpreted_data(self):
#        plugin = PaymentMethod.get_model(self.method)
        #exec "from payment.gateways.%s.interpreter import Transaction as interpreter" % (self.method)
        return self.method.get_plugin().transaction_interpreter(self)

    @property
    def contact(self):
        return self.bill.contact
    
    def confirm(self):
        self.status = settings.CONFIRMED
        self.save()
    
    def reject(self):
        self.status = settings.REJECTED
        self.save()


@receiver(bill_pre_send, sender=Bill, dispatch_uid="payment.create_transaction")
def create_transaction(sender, **kwargs):
    bill = kwargs['bill']
    Transaction.create(bill)

