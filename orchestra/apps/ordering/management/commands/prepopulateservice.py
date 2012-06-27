from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import models
from django.utils.translation import ugettext as _
from ordering import settings
from ordering.models import ServiceAccounting, Tax


class Command(BaseCommand):
    def handle(self, created_models, **options):
        verbosity = int(options.get('verbosity', 1))
        for model in created_models:
            #if Service in model.__bases__:
            ct = ContentType.objects.get_for_model(model)
            if model._meta.module_name == 'domain':
                from settings import EXTENSION_CHOICES
                for choice in EXTENSION_CHOICES:
                    ServiceAccounting(description='Domain %s' % (choice[0].upper()),
                            content_type=ct,
                            expression="O['instance']['extension']=='%s'" % (choice[0]),
                            billing_period=settings.ANUAL,
                            billing_point=settings.VARIABLE,
                            payment=settings.PREPAY,
                            on_prepay="",
                            discount="",
                            pricing_period=settings.ANUAL,
                            pricing_point=settings.VARIABLE,
                            pricing_effect=settings.CURRENT,
                            pricing_with=settings.ORDERS,
                            metric='',
                            weight_with=settings.NO_WEIGHT,
                            orders_with=settings.REGISTRED_OR_RENEWED,
                            rating=settings.CONSERVATIVE,
                            tax=None,
                            is_fee=False,
                            active=False).save()   
            if model._meta.module_name == 'systemuser':
                    ServiceAccounting(description='FTP User',
                            content_type=ct,
                            expression="O['instance']['ftp_only']==True",
                            billing_period=settings.ANUAL,
                            billing_point=settings.FIXED,
                            payment=settings.PREPAY,
                            on_prepay="%s,%s,%s,%s" % (settings.REFOUND_ON_CANCEL, 
                                                       settings.RECHARGE_ON_CANCEL, 
                                                       settings.REFOUND_ON_DISABLE, 
                                                       settings.RECHARGE_ON_DISABLE),
                            discount="%s,%s,%s" % (settings.DISCOUNT_ON_CANCEL, 
                                                   settings.DISCOUNT_ON_REGISTER, 
                                                   settings.DISCOUNT_ON_DISABLE),
                            pricing_period=settings.NO_PERIOD,
                            pricing_point=settings.NO_PERIOD,
                            pricing_effect=settings.NO_PERIOD,
                            pricing_with=settings.ORDERS,
                            metric='',
                            weight_with=settings.NO_WEIGHT,
                            orders_with=settings.ACTIVE,
                            rating=settings.BEST,
                            tax=None,
                            is_fee=False,
                            active=False).save()
                    ServiceAccounting(description='System User',
                            content_type=ct,
                            expression="O['instance']['ftp_only']==False",
                            billing_period=settings.ANUAL,
                            billing_point=settings.FIXED,
                            payment=settings.PREPAY,
                            on_prepay="%s,%s,%s,%s" % (settings.REFOUND_ON_CANCEL, 
                                                       settings.RECHARGE_ON_CANCEL, 
                                                       settings.REFOUND_ON_DISABLE, 
                                                       settings.RECHARGE_ON_DISABLE),
                            discount="%s,%s,%s" % (settings.DISCOUNT_ON_CANCEL, 
                                                   settings.DISCOUNT_ON_REGISTER, 
                                                   settings.DISCOUNT_ON_DISABLE),
                            pricing_period=settings.NO_PERIOD,
                            pricing_point=settings.NO_PERIOD,
                            pricing_effect=settings.NO_PERIOD,
                            pricing_with=settings.ORDERS,
                            metric='',
                            weight_with=settings.NO_WEIGHT,
                            orders_with=settings.ACTIVE,
                            rating=settings.BEST,
                            tax=None,
                            is_fee=False,
                            active=False).save()
            if model._meta.module_name == 'virtualuser':                                
                    ServiceAccounting(description='Mail User',
                            content_type=ct,
                            expression="True",
                            billing_period=settings.ANUAL,
                            billing_point=settings.FIXED,
                            payment=settings.PREPAY,
                            on_prepay="%s,%s,%s,%s" % (settings.REFOUND_ON_CANCEL, 
                                                       settings.RECHARGE_ON_CANCEL, 
                                                       settings.REFOUND_ON_DISABLE, 
                                                       settings.RECHARGE_ON_DISABLE),
                            discount="%s,%s,%s" % (settings.DISCOUNT_ON_CANCEL, 
                                                   settings.DISCOUNT_ON_REGISTER, 
                                                   settings.DISCOUNT_ON_DISABLE),
                            pricing_period=settings.NO_PERIOD,
                            pricing_point=settings.NO_PERIOD,
                            pricing_effect=settings.NO_PERIOD,
                            pricing_with=settings.ORDERS,
                            metric='',
                            weight_with=settings.NO_WEIGHT,
                            orders_with=settings.ACTIVE,
                            rating=settings.BEST,
                            tax=None,
                            is_fee=False,
                            active=False).save()                                                              

        if verbosity >= 1:
            self.stdout.write("ServiceAccounting prepopulated successfully.\n")
         
