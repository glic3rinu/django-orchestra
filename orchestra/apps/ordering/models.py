from common.collector import DependencyCollector
from common.fields import MultiSelectField
from common.utils.models import group_by, generate_chainer_manager
from datetime import datetime
import decimal
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from heapq import merge
from helpers import best_pricing, conservative_pricing, _get_pending_billing_periods, _create_bills, _get_price
import settings
from utils import get_next_point, DateTime_conv, Period, get_prev_point


class Pack(models.Model):
    """ 
        A pack consists on a different collections of included services.
        For example, "Membership quota" will be there, as like as special traffic 
        contracts, "staff accounts", or any kind of promotional pack.  
    """
    name = models.CharField(max_length=32, unique=True)
    allow_multiple = models.BooleanField(default=False, help_text=_("allow multiple packs per contact, WARNING: ALLOW MULTIPLE NOT SUPORTED"))

    def __unicode__(self):
        return self.name


class ContractedPackQuerySet(models.query.QuerySet):
    def active(self, *args, **kwargs):
        return self.exclude(cancel_date__isnull=False, cancel_date__lt=datetime.now()).filter(*args, **kwargs)


class ContractedPack(models.Model):
    pack = models.ForeignKey(Pack)
    contact = models.ForeignKey(settings.CONTACT_MODEL)
    register_date = models.DateTimeField(auto_now_add=True)
    cancel_date = models.DateTimeField(null=True)
    
    objects = generate_chainer_manager(ContractedPackQuerySet)
    
    def __unicode__(self):
        return self.pack.name

    def save(self, *args, **kwargs):
        if not self.pack.allow_multiple:
            if self.__class__.objects.active(pack=self.pack, contact=self.contact).count() > 0:
                raise ValidationError('Only one pack per contact is allowed.')
        super(ContractedPack, self).save(*args, **kwargs)


# Provide contact accessor if it is different from contact
if 'contact' != settings.CONTACT_FIELD:
    @property
    def contact(self):
        return self.contact
    setattr(ContractedPack, settings.CONTACT_FIELD, contact)


class ServiceAccounting(models.Model):
    """
        Different services provided by the ISP. The label atribute is used to 
        identify the service, and relate them with a Service class.
        A non billable service won't be considered when generating the invoices.
        Limitations: Because of bill must have a contract, there is no native suppor 
                    for bill all contact traffic together or all web maintainance hours per contact. 
                    If you want to do that your app must support this kind of stuff or
                    you can do a 'hack' with rosource app to handle per contact service weight. 
    """
    description = models.CharField("service description", max_length=50, unique=True)
    content_type = models.ForeignKey(ContentType)
    expression = models.CharField(max_length=255, help_text=_("format: O['field1']=='value' and (O['field2']=='value2' or O['field3' == True)"))
    # BILLING
    billing_period = models.IntegerField(choices=settings.PERIOD_CHOICES, 
        default=settings.DEFAULT_BILLING_PERIOD, help_text=_("Renew period for recurring invoicing"))
    billing_point = models.IntegerField(default=settings.DEFAULT_BILLING_POINT, choices=settings.POINT_CHOICES,
        help_text=_(""" If VARIABLE: billing period points on order.register_date, 
                        If FIXED billing period points on a default month and day, """))
    payment = models.CharField(max_length=1, choices=settings.PAYMENT_CHOICES, default=settings.DEFAULT_PAYMENT)
    #discount = models.CharField(max_length=32, choices=settings.DISCOUNT_CHOICES, default=settings.DEFAULT_DISCOUNT)
    on_prepay = MultiSelectField(max_length=32, choices=settings.ON_PREPAY_CHOICES, default=settings.DEFAULT_ON_PREPAY, blank=True, help_text=_('After billing'))
    discount = MultiSelectField(max_length=32, choices=settings.DISCOUNT_CHOICES, default=settings.DEFAULT_DISCOUNT, blank=True, help_text=_('Before billing'))
    # PRICING
    pricing_period = models.IntegerField(choices=settings.PERIOD_CHOICES, 
        default=settings.DEFAULT_PRICING_PERIOD, help_text=_("In what period do you want to lookup for calculating price?"))
    pricing_point = models.IntegerField(choices=settings.POINT_CHOICES, 
        default=settings.DEFAULT_PRICING_POINT, help_text=_("In what moment do you want to lookup for calculating price?"))
    pricing_effect = models.IntegerField(choices=settings.PRICING_EFFECT_CHOICES, 
        default=settings.DEFAULT_PRICING_EFFECT, help_text=_("In what position do you want to apply the pricing period?"))
    pricing_with = models.CharField(max_length=1,default=settings.DEFAULT_PRICING_WITH, choices=settings.PRICING_WITH_CHOICES)        
    orders_with = models.CharField(max_length=1, default=settings.DEFAULT_ORDERS_WITH, choices=settings.ORDERS_WITH_CHOICES)
    weight_with = models.CharField(max_length=1, default=settings.DEFAULT_WEIGHT_WITH, choices=settings.WEIGHT_WITH_CHOICES)
    metric = models.CharField(max_length=128, blank=True, help_text=_("format: O['field1'] - O['field2']. If null metric is the number of orders."))   
    metric_get = models.CharField(max_length=16, blank=True, default=settings.DEFAULT_METRIC_GET, choices=settings.METRIC_GET_CHOICES)
    metric_discount = models.ForeignKey('self', null=True, blank=True, 
        help_text=_(""" make a discount, for example on traffic prepay, target needs to have pricing_period, 
                        bill period is required for both, only with single order """))   
    rating = models.CharField(max_length=1, choices=settings.RATING_CHOICES, default=settings.DEFAULT_RATING)
#    default_price = models.DecimalField(max_digits=12, decimal_places=2, 
#        help_text:_('price used if no ratings, and for discounts estimation'))
    tax = models.ForeignKey('ordering.Tax', default=settings.DEFAULT_TAX_PK, null=True)
    is_fee = models.BooleanField("is membership fee?", default=settings.DEFAULT_IS_FEE, 
        help_text="select this if this service is a membership fee" )
    active = models.BooleanField("is active?", default=True)
    
    def __unicode__(self):
        return self.description    
    
    def disable(self):
        #TODO: when disable/active a service a new order is genered, but if it has been billed 
        # maybe it make a mess.
        self.active = False
        self.save()

    def activate(self):
        self.active = True
        self.save()
    
    def fetch(self):
        for obj in self.content_type.model_class().objects.all():
            Order.update_orders(obj)
    
    @property
    def prepayment(self):
        if self.payment == settings.PREPAYMENT: return True
        else: return False
    
    @property
    def postpayment(self):
        if self.payment == settings.POSTPAYMENT: return True
        else: return False
    
    def _expression_match(self, O):
        """ return true if an O (object) match with service attributes """
        return eval(self.expression)        

    @classmethod
    def get_active(cls, obj):
        """ Given an object and their ContentType return their Service instance. """
        ct = ContentType.objects.get_for_model(obj)
        services = []
        for service in cls.objects.filter(content_type=ct, active=True):
            try: result = service._expression_match(obj)
            except: pass
            else: 
                if result:            
                    services.append(service)
        return services

    # TODO: find out a more consistent and cool way to get all this config parameters:

    @property
    def refound_on_cancel(self):
        return True if settings.REFOUND_ON_CANCEL in self.on_prepay else False
        
    @property
    def refound_on_disable(self):
        return True if settings.REFOUND_ON_DISABLE in self.on_prepay else False
        
    @property
    def refound_on_weight(self):
        return True if settings.REFOUND_ON_WEIGHT in self.on_prepay else False
        
    @property
    def recharge_on_disable(self):
        if settings.RECHARGE_ON_DISABLE in self.on_prepay: return True
        else: return False

    @property
    def recharge_on_cancel(self):
        if settings.RECHARGE_ON_CANCEL in self.on_prepay: return True
        else: return False
    
    @property
    def recharge_on_weight(self):
        return True if settings.RECHARGE_ON_WEIGHT in self.on_prepay else False
        
    @property
    def discount_on_register(self):
        return True if settings.DISCOUNT_ON_REGISTER in self.discount else False
        
    @property
    def discount_on_disable(self):
        return True if settings.DISCOUNT_ON_DISABLE in self.discount else False
        
    @property
    def discount_on_cancel(self):
        return True if settings.DISCOUNT_ON_CANCEL in self.discount else False
        
    @property
    def pricing_with_weight(self):
        return True if self.pricing_with == settings.WEIGHT else False

    @property
    def pricing_with_orders(self):
        return not self.pricing_with_weight

    @property
    def is_postpay(self):
        return True if self.payment == settings.POSTPAY else False

    @property
    def is_prepay(self):
        return True if self.payment == settings.PREPAY else False

    @property
    def has_pricing_period(self):
        if self.pricing_period != settings.NO_PERIOD: return True
        else: return False
    
    @property
    def has_billing_period(self):
        if self.billing_period != settings.NO_PERIOD: return True
        else: return False
        
    @property        
    def orders_with_is_active(self):
        if self.orders_with == settings.ACTIVE : return True
        else: return False
        
    @property    
    def orders_with_is_active_or_billed(self):
        if self.orders_with == settings.ACTIVE_OR_BILLED : return True
        else: return False
        
    @property
    def orders_with_is_renewed(self):
        if self.orders_with == settings.RENEWED : return True
        else: return False
        
    @property
    def orders_with_is_registred(self):
        if self.orders_with == settings.REGISTRED : return True
        else: return False
        
    @property
    def orders_with_is_registred_or_renewed(self):  
        if self.orders_with == settings.REGISTRED_OR_RENEWED : return True
        else: return False
        
    @property
    def weight_with_is_single_order(self):  
        if self.weight_with == settings.SINGLE_ORDER: return True
        else: return False

    @property
    def weight_with_is_all_orders(self):  
        if self.weight_with == settings.ALL_ORDERS: return True
        else: return False    
        
    @property
    def rating_with_best_price(self):
        if self.rating == settings.BEST: return True
        else: return False
        
    @property
    def rating_with_conservative_price(self):
        if self.rating == settings.CONSERVATIVE: return True
        else: return False
    
    @property
    def billing_is_fixed(self):
        if self.billing_point == settings.FIXED: return True
        else: return False
            
    @property
    def pricing_is_fixed(self):
        if self.pricing_point == settings.FIXED: return True
        else: return False

    @property
    def pricing_is_variable(self):
        return not self.pricing_is_fixed
    
    @property
    def pricing_effect_is_current(self):
        if self.pricing_effect == settings.CURRENT: return True
        else: return False
    
    @property
    def pricing_effect_is_every(self):
        if self.pricing_effect == settings.EVERY: return True
        else: return False        
    
    def _split_period(self, ini, end, period, fixed, point):
        start_date = DateTime_conv(ini)
        end_date = DateTime_conv(end)
        initial, incremental = get_next_point(period, fixed, start_date, var_point=point)
      
        if initial > end_date: return [Period(ini, end)]
        # Incomplete first period. 
        else: periods = [Period(ini, datetime.fromtimestamp(initial))]

        while initial < end_date:
            next = initial + incremental
            if next > end_date: next = end_date
            periods.append(Period(datetime.fromtimestamp(initial), 
                                  datetime.fromtimestamp(next)))      
            initial = next   
        return periods            
    
    def split_pricing_period(self, ini, end, point=None):
        if self.pricing_effect_is_current:
            initial, incremental = get_next_point(period, fixed, start_date, var_point=point)
            return [Period(datetime.fromtimestamp(initial - (incremental)), 
                           datetime.fromtimestamp(initial))]
        return self._split_period(ini, end, self.pricing_period, self.pricing_is_fixed, point)
        
    def split_billing_period(self, ini, end, point=None):
        return self._split_period(ini, end, self.billing_period, self.billing_is_fixed, point)
        
    def get_metric(self, O):
        if self.pricing_with_weight:
            return eval(self.metric)
        else: raise TypeError('This service is not configured with pricing weight') 
        return metric
    
    def get_price(self, contact, rating_metric, start_metric=1, end_metric=None, start_date=None, end_date=None):
        """ start and end are optional if you want to specify kind of range: 
                price of order (4-4)/10, 
                price for hours (50-60)/60
            date used for get the active packs between this period
        """ 
        if not end_metric: end_metric = rating_metric
        
        pack_pks = self.rate_set.exclude(pack__isnull=True).values_list('pack__pk', flat=True).distinct()
        # Get Pack contraction cancel changes. 
        #TODO: and disables?
        Contract = contact.contract.__class__
        contracts = Contract.objects.filter_active_during_with_contact_model_pks(contact, Pack, pack_pks, start_date, end_date)
        cancels = []
        for contract in contracts:
            cancels = list(merge(contract.get_cancel_dates(lt=end_date), cancels))
        #cancels = contracts.filter(cancel_date__lt=end_date).values_list('cancel_date', flat=True)
        registers = contracts.filter(register_date__gt=start_date).values_list('register_date', flat=True)
        changes = list(merge([start_date], cancels, registers, [end_date]))
        changes.sort()
        u_changes = [changes[0]]
        for ix in range(len(changes)-1): 
            if changes[ix] != changes[ix+1]: u_changes.append(changes[ix+1])
        changes = u_changes
        final_price = 0
        for ix in range(len(changes)-1):
            ini = changes[ix]
            end = changes[ix+1]
            total_period = DateTime_conv(end_date) - DateTime_conv(start_date)
            percentil = decimal.Decimal(str((DateTime_conv(end) - DateTime_conv(ini)).seconds/total_period.seconds))
            contracts = Contract.objects.filter_active_during_with_contact_model_pks(contact, Pack, pack_pks, ini, end)
            packs = [contract.content_object for contract in contracts]
            
            rates = Rate.get_rates(self, packs, rating_metric)
            ix = 0
            price = 0
            acumulated = 0

            while acumulated < start_metric:
                acumulated += rates[ix]['number']
                ix += 1
            
            if acumulated >= start_metric: 
                if acumulated > end_metric: acumulated = end_metric
                num = (acumulated - start_metric) + 1
                price = num * rates[ix-1]['price']
                #acumulated += (num-1)        
            
            while acumulated < end_metric:
                ant_acumulated = acumulated
                acumulated += rates[ix]['number']
                if acumulated >= end_metric: 
                    price += (end_metric - ant_acumulated) * rates[ix]['price']
                else: price += rates[ix]['number'] * rates[ix]['price']
                ix +=1
            
            final_price += price * percentil

        return final_price


class Tax(models.Model):
    """ Expresses the different taxes charged to the services """
    name = models.CharField(max_length=15)
    value = models.DecimalField(max_digits=4, decimal_places=2)	

    def __unicode__(self):
        return self.name + ' ' + str(self.value) + '%'
      


class Rate(models.Model):
    """ 
        Different prices that are charged for provisioning a service based on 
        the number of orders and type of Service Pack.
        Default tariff when pack is NULL
    """

    pack = models.ForeignKey('Pack', null=True, blank=True)
    service = models.ForeignKey(ServiceAccounting)
    metric = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("pack", "service", "metric")		

    def __unicode__(self):
        if not self.pack: Name = 'default'
        else: Name = self.pack.name
        return Name+"--"+self.service.description+"--"+str(self.metric)


    @classmethod
    def get_rates(cls, service, packs, metric):
        """ Return list of rates: {'number', 'price'} for service and packs that fits with metric """
        
        #TODO: Multiple Pack support
        # Default pack always is used.
        qset = Q(pack__isnull=True)
        for pack in packs:
            qset |= Q(pack=pack)
        rates = cls.objects.filter(Q(service=service, metric__lte=metric) & qset)
        if not rates: raise ValueError("There is no available price for this service")
        rates = rates.order_by('metric').order_by('pack')
        if service.rating_with_best_price:
            return best_pricing(rates, metric)
        elif service.rating_with_conservative_price:
            return conservative_pricing(rates, metric)
        else: raise ValueError('There is no available rating algorithm')
        


class OrderQuerySet(models.query.QuerySet):
    def not_ignored(self):
        return self.exclude(ignore=True)

    def by_object(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return self.filter(object_id=obj.pk, content_type=ct)

    def pending_of_bill(self, point=datetime.now()):
        """ return pending of bill orders """
        #TODO: Performance booster with fixed period orders
        #TODO: ignore disabled
        
        pending_subset_pks = self.not_ignored().filter(last_bill_date__isnull=True).values_list('pk', flat=True)
        re_pending_subset_pks = []
        for order in self.not_ignored().filter(~Q(last_bill_date__gte=F('cancel_date'))|Q(last_bill_date__lt=F('billed_until'))).exclude(pk__in=pending_subset_pks):
            if order.has_pending_periods(point): re_pending_subset_pks.append(order.pk)
        
        pending_subset_pks.extend(re_pending_subset_pks)
        orders_subset = self.not_ignored().exclude(pk__in=pending_subset_pks)
        p_orders_subset = []
        for order in orders_subset:
            if order.billed_until < order.get_next_billing_point(point):
                p_orders_subset.append(order.pk)
        pending_subset_pks.extend(p_orders_subset)
        return self.filter(pk__in=pending_subset_pks)
        
    def metric_with_orders(self):
        return self.filter(service__pricing_with=settings.ORDERS)    
    
    def metric_with_weight(self):
        return self.filter(service__pricing_with=settings.WEIGHT)
        
    def weight_with_all_contact_orders(self):
        return self.filter(service__weight_with=settings.ALL_CONTACT_ORDERS)
    
    def pending_by_contact(self, contact):
    
        """ return pending of bill orders for Contact """
        return self.pending_of_bill().filter(contact=contact)
    
    def pending_services_by_contact(self, contact):
        """ return a service list of pending of bill service for given contact """
        services = self.pending_by_contact(contact).values('service').distinct()
        return self.filter(pk__in=services)            

    def active(self, *args, **kwargs):
        """ return active orders """
        return self.filter(Q(cancel_date__isnull=True)|Q(cancel_date__gt=datetime.now())).filter(*args, **kwargs)
    
    def disabled_during(self, ini, end):
        return self.filter(Q(contract__deactivationperiod__start_date__lte=ini) &
                    Q(Q(contract__deactivationperiod__end_date__isnull=True)| 
                      Q(contract__deactivationperiod__end_date__gte=end)) &
                    Q(Q(contract__deactivationperiod__annulation_date__isnull=True) |
                      Q(contract__deactivationperiod__annulation_date__gt=end))).distinct()


    def billing_activity_during(self, periods, service):
        qset = Q()
        for period in periods:
            if not service.refound_on_cancel and service.discount_on_cancel:
                partial_qset = Q(Q(register_date__lt = period.end) & 
                    Q(Q(cancel_date__isnull=True) | Q(cancel_date__gt = period.ini) | Q(billed_until__gt = period.ini)))
            else: partial_qset = Q(Q(register_date__lt = period.end) & 
                    Q(Q(cancel_date__isnull=True) | Q(cancel_date__gt = period.ini)))
            if service.billing_is_fixed and not service.discount_on_register:
                ini = get_prev_billing_point(period.ini)
                end = get_next_billing_point(period.end)
                partial_qset |= Q(register_date__gte=ini, register_date__lt=end)
            if service.billing_is_fixed and not service.discount_on_cancel:
                ini = get_prev_billing_point(period.ini)
                end = get_next_billing_point(period.end)
                partial_qset |= Q(cancel_date__lte=end, cancel_date__gt=ini) 
            if not service.billing_is_fixed and not service.discount_on_cancel:
                incremental = get_relative_period(service.billing_period)
                point = DateTime_conv(period.ini) - incremental
                point = datetime.fromtimestamp(point)
                partial_qset |= Q(cancel_date__gt=point, cancel_date__lte=period.end)
            if service.discount_on_disable:
                exclude = self.disabled_during(period.ini, period.end).values_list('pk', flat=True)
                partial_qset &= ~Q(pk__in=exclude)                
            qset |= Q(partial_qset)

        return self.filter(qset).distinct()

    def registred_during(self, periods, service):
        """ return the orders that has been registred between ini and end """
        
        inf = 'register_date__gte' if service.pricing_effect_is_every else 'register_date__gt'
        sup = 'register_date__lte' if service.pricing_effect_is_current else 'register_date__lt'
    
        qset = Q()
        for period in periods:
            qset |= Q(**{sup:period.end, inf:period.ini})
              
        return self.filter(qset)
        
        
    def renewed_during(self, periods, service):
        """ return recurring orders that their renew date is within ini and end """
        #TODO: add suport is disable when renewed? 
        #TODO: Make more efficient for fixed periods.
        
        #if service.billing_is_fixed:  
        #    pass
            # if ini-end match with billing point return all active
            # else return 0
        #else:
        
        inf = '>=' if service.pricing_effect_is_every else '>'
        sup = '<=' if service.pricing_effect_is_current else '<'

        order_pks = []
        for period in periods:
            for order in self.exclude(cancel_date__lt=period.ini):
                for renew in order.get_renew_dates(period.end):
                    if eval("renew %s period.end and renew %s period.ini" % (sup, inf)):
                        order_pks.append(order.pk)    
        return self.filter(pk__in=order_pks)

    def registred_or_renewed_during(self, periods, service):
        pks = []
        for period in periods:

            reg_pks = self.registred_during([period], service).values_list('pk', flat=True)
            ren_pks = self.renewed_during([period], service).values_list('pk', flat=True)
            pks.extend(reg_pks)
            pks.extend(ren_pks)
        return self.filter(pk__in=pks)

                        
    def get_active(self, service, contract):
        if service.content_type: qset = self.active(contract=contract, service=service)
        else: qset = self.active(contact=contract.contact, service=service)
        if len(qset) != 1: 
            raise self.model.MultipleObjectsReturned("Order.objects.get_active() must return one element")
        else: return qset[0]



class Order(models.Model):
    #TODO: add support for negative prices (discounts) play with canceldate&billeduntil in order to ensure discount apply
    contact = models.ForeignKey(settings.CONTACT_MODEL)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True)
    service = models.ForeignKey(ServiceAccounting)
    #TODO: DEBUG prupose only.
    register_date = models.DateTimeField()
    #register_date = models.DateTimeField(auto_now_add=True)
    cancel_date = models.DateTimeField(null=True, blank=True)
    last_bill_date = models.DateTimeField(null=True, blank=True)
    billed_until = models.DateTimeField(null=True, blank=True)
    ignore = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True)

    content_object = generic.GenericForeignKey()
    objects = generate_chainer_manager(OrderQuerySet)

    class Meta:
        ordering = ['-id']
        #ordering = ['-register_date']

    def __unicode__(self):
        return "%s(%s)" % (self.service, self.content_object)

    @classmethod
    def create(cls, obj, service, contact=None):
        ct = ContentType.objects.get_for_model(obj)
        if not contact:
            contact = getattr(obj, settings.CONTACT_FIELD)
        description = "%s: %s" % (service, obj)
        order = cls.objects.create(object_id=obj.pk, content_type=ct, contact=contact,
                                   service=service, description=description)
        if service.pricing_with_weight:      
            metric = service.get_metric(obj)
            MetricStorage.record(order=order, value=metric)


    def update(self):
        if self.service.pricing_with_weight:
            instance = self.content_object      
            metric = self.service.get_metric(instance)
            MetricStorage.record(order=self, value=metric)
        description = "%s: %s" % (self.service, self.content_object)
        if self.description != description:
            self.description = description
            self.save()

    @classmethod
    def update_orders(cls, instance):
        try: contact = getattr(instance, settings.CONTACT_FIELD)
        except: return 

        # Optimization
        if not ServiceAccounting.objects.filter(content_type__name=instance._meta.verbose_name_raw): return
        before_services = []
        for service_pk in Order.objects.by_object(instance).active().values_list('service', flat=True).distinct():
            before_services.append(ServiceAccounting.objects.get(pk=service_pk))    

        after_services = ServiceAccounting.get_active(instance)
        intersection = set(before_services).intersection(after_services)
        
        # After - Intersection    
        for service in set(after_services) - intersection:
            Order.create(instance, service)
        
        # Old - Intersection
        for service in set(before_services) - intersection:
            Order.objects.by_object(instance).active().get(service=service).cancel()
                
        # Intersection        
        for service in intersection:
            Order.objects.by_object(instance).active().get(service=service).update()

    @property
    def tax(self):
        return self.service.tax

    #DEBUG prupose only
    def save(self, *args, **kwargs):
        if not self.pk:
            self.register_date = datetime.now()
        super(Order, self).save(*args, **kwargs)

    def has_pending_periods(self, point=datetime.now()):
        if not self.last_bill_date: return True
        elif self.cancel_date:
            if self.cancel_date <= self.last_bill_date: return True
        next_point = self.get_next_billing_point(point)
        if next_point > self.billed_until: return True
        refound, recharge = get_recharge_and_refound_periods(self)
        if refound or recharge: return True
        else: return False
                
    def _cancel_date(self):
        return self.cancel_date if self.cancel_date else self.contract.cancel_date

    @property
    def metric(self):
        #TODO: remove thsi shit
        try: return MetricStorage.objects.get_last(self).value
        except self.DoesNotExist: return 1

    def get_metrics(self, ini, end):
        return MetricStorage.objects.filter_during(self, ini, end)

    def get_metric(self, ini, end):
        if self.service.pricing_with_orders: return 1
        else: return MetricStorage.get_during(self, ini, end)
    
    def get_payed(self, ini, end): pass
    
    def get_bill(self, date): pass
        
    def active_periods_during(self, period): 
        from utils import Period
        next_ini = period.ini
        active_periods = []
        for d_period in self.contract.get_disabled_periods_during(period):
            #FIXME: d_periods.end_date can be None!!
            if next_ini < d_period.start_date:
                active_periods.append(Period(next_ini, d_period.start_date))
            next_ini = min(period.end_date, d_period.end_date)
        if next_ini != period.end:
            active_periods.append(Period(next_ini, period.end))
        return active_periods

    def get_renew_dates(self, point):
        if not self.service.billing_is_fixed: ini = self.register_date
        else: ini = self.get_prev_billing_period(self.register_date)
        end = self.get_next_billing_point(point)
        renews = [period.end for period in self.service.split_billing_period(ini, end) ] 
        return renews
    
    @property
    def pricing_period(self):
        return self.service.pricing_period       
       
    def cancel(self):
        self.cancel_date = datetime.now()
        self.save()
        
    @classmethod
    def bill_contact(cls, contact, commit=False):
        orders = cls.objects.pending_of_bill(contact=contact)
        return _bill(contact, orders, orders, commit)
        
    @classmethod
    def bill_orders(cls, billing_orders, pricing_orders=None, point=datetime.now(), 
                    fixed_point=False, force_next=False, create_new_open=False, commit=False):
        if pricing_orders is None: pricing_orders=billing_orders
        c_billing_orders = group_by(cls, 'contact', billing_orders, dictionary=True)
        c_pricing_orders = group_by(cls, 'contact', pricing_orders, dictionary=True)
        bills = []
        for contact in c_billing_orders:
            _bills = _create_bills(cls, contact, c_billing_orders[contact], 
                        c_pricing_orders[contact], point=point, fixed_point=fixed_point, 
                        force_next=force_next, create_new_open=create_new_open, commit=commit)
            bills.extend(_bills)
        return bills            

    def get_price(self, orders, bill_period, active_period):
        """ Return price for the period a_ini-a_end of total b_ini-b_end """
        price = _get_price(self, orders, bill_period, active_period)
        return round(price, 2)

    def get_prev_pricing_point(self, date, lt=False):
        service = self.service
        prev, increment = get_prev_point(service.pricing_period, service.pricing_is_fixed, date, var_point=self.register_date)
        if lt and date == prev: return datetime.fromtimestamp(prev - increment)
        return datetime.fromtimestamp(prev)
        
    def get_prev_billing_point(self, date):
        service = self.service
        prev, increment = get_prev_point(service.billing_period, service.billing_is_fixed, date, var_point=self.register_date)
        return datetime.fromtimestamp(prev)
        
    def get_next_pricing_point(self, date):
        service = self.service
        next, increment = get_next_point(service.pricing_period, service.pricing_is_fixed, date, var_point=self.register_date)
        return datetime.fromtimestamp(next)
        
    def get_next_billing_point(self, date, fixed=None):
        service = self.service
        if fixed == None:
            fixed = service.billing_is_fixed
        next, increment = get_next_point(service.billing_period, fixed, date, var_point=self.register_date)
        return datetime.fromtimestamp(next)

    def get_pending_billing_periods(self, point=datetime.now(), fixed_point=False, force_next=False):
        """ Return entair pending billing periods and their active periods per billing period. """
        return _get_pending_billing_periods(self, point, fixed_point, force_next)

    def disabled_on(self, date):
        return self.contract.disabled_on(date)

class MetricStorageManager(models.Manager):
    def get_last(self, order):
        """ return last metric """
        try: return self.filter(order=order)[0]
        except IndexError: raise order.DoesNotExist
        
    def filter_during(self, order, ini, end):
        return self.filter(order=order, date__lte=end, date__gte=ini)

    def get_during(self, order, ini, end):
        return self.get(order=order, date__lte=end, date__gte=ini)

class MetricStorage(models.Model):
    """ Storage metric of orders that has _by_weight, 
        WARN: In order to keep this simple and clean:
            If order has pricing period metricstorage overrides their period value for the provided. 
            so, your app should to take care of providing a correct value for the pricing period. 
        LIMITATIONS: you can't change a pricing period without problems :( unless you bill all related stuff
        #TODO: display warn in service form if pricing period has been changed
    """ 
    order = models.ForeignKey(Order)
    value = models.BigIntegerField()
    date = models.DateTimeField()                       

    objects = MetricStorageManager()
    
    def __unicode__(self):
        return str(self.order)
    
    class Meta:
        ordering = ['-date']

    @property
    def start_date(self):
        return self.date
        
    @property
    def end_date(self):
        try: return MetricStorage.objects.filter(order=self.order, date__gt=self.date).order_by('date')[0].date
        except IndexError: return None

    @classmethod
    def get_during(cls, order, ini, end):
        """ Return metrics active during ini and end """
        
        algorithm = order.service.metric_get
        if algorithm == 'LAST':
            return cls.objects.filter(order=order, date__lte=end)[0].value
        elif algorith == 'CHANGES':
            return cls.objects.get_during(order=order, ini=ini, end=end).value
        else:
            exec "from django.db.models import %s as operation" % algorithm
            return cls.objects.filter_during(order=order, ini=ini, end=end).aggregate(operation('value')).values()[0]

    @classmethod
    def record(cls, order, value):
        if value is None: value = 0
        qset = cls.objects.filter(order=order).order_by('-date')
        #if qset.count() == 0 or qset[0].value != value:
        cls.objects.create(order=order, value=value, date=datetime.now())


# We listen to all post_deletes in order to cancel the orders owned by the object
@receiver(post_delete, dispatch_uid="ordering.cancel_orders")
def cancel_orders(sender, **kwargs):
    instance = kwargs['instance']
    
    if ServiceAccounting.objects.filter(content_type__name=instance._meta.verbose_name_raw):
        for order in Order.objects.by_object(instance).active():
            order.cancel()
    
    #TODO check if this deletion affects other orders
    #update_orders(sender=sender, instance=instance)


# We listen to all model post_save and try to update orders with all their dependencies,
# this will work event with contract approach, because eventually contract will be created
# and content_object will pop up as one of their dependencies
@receiver(post_save, dispatch_uid="ordering.update_orders_model")
def update_orders(sender, **kwargs):
    instance = kwargs['instance']
    # avoid enter on infinite loop 
    # since update_orders may trigger a MetricStorage and Order post_save this will never end.
    if not (isinstance(instance, MetricStorage) or isinstance(instance, Order)):
        for dependency in DependencyCollector(instance, weak=True).objects.keys():
            Order.update_orders(dependency)
        
