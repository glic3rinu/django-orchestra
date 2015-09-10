import datetime

from celery.task.schedules import crontab
from django.apps import apps

from orchestra.contrib.tasks import periodic_task

from . import settings


@periodic_task(run_every=crontab(hour=4, minute=30), name='orders.cleanup_metrics')
def cleanup_metrics():
    from .models import MetricStorage, Order
    Service = apps.get_model(settings.ORDERS_SERVICE_MODEL)
    
    # General cleaning: order.billed_on-delta
    general = 0
    delta = datetime.timedelta(days=settings.ORDERS_BILLED_METRIC_CLEANUP_DAYS)
    for order in Order.objects.filter(billed_on__isnull=False):
        epoch = order.billed_on-delta
        try:
            latest = order.metrics.filter(updated_on__lt=epoch).latest('updated_on')
        except MetricStorage.DoesNotExist:
            pass
        else:
            general += order.metrics.exclude(pk=latest.pk).filter(updated_on__lt=epoch).count()
            order.metrics.exclude(pk=latest.pk).filter(updated_on__lt=epoch).only('id').delete()
    
    # Reduce monthly metrics to latest
    monthly = 0
    monthly_services = Service.objects.exclude(metric='').filter(
        billing_period=Service.MONTHLY, pricing_period=Service.BILLING_PERIOD
    )
    for service in monthly_services:
        for order in Order.objects.filter(service=service):
            dates = order.metrics.values_list('created_on', flat=True)
            months = set((date.year, date.month) for date in dates)
            for year, month in months:
                metrics = order.metrics.filter(
                    created_on__year=year, created_on__month=month,
                    updated_on__year=year, updated_on__month=month)
                try:
                    latest = metrics.latest('updated_on')
                except MetricStorage.DoesNotExist:
                    pass
                else:
                    monthly += metrics.exclude(pk=latest.pk).count()
                    metrics.exclude(pk=latest.pk).only('id').delete()
    
    return (general, monthly)
