import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models.loading import get_model
from django.utils import timezone

from orchestra.models.utils import get_model_field_path

from .backends import ServiceMonitor


def compute_resource_usage(data):
    """ Computes MonitorData.used based on related monitors """
    from .models import MonitorData
    resource = data.resource
    today = timezone.now()
    result = 0
    has_result = False
    for monitor in resource.monitors:
        # Get related dataset
        resource_model = data.content_type.model_class()
        monitor_model = get_model(ServiceMonitor.get_backend(monitor).model)
        if resource_model == monitor_model:
            dataset = MonitorData.objects.filter(monitor=monitor,
                    content_type=data.content_type_id, object_id=data.object_id)
        else:
            path = get_model_field_path(monitor_model, resource_model)
            fields = '__'.join(path)
            objects = monitor_model.objects.filter(**{fields: data.object_id})
            pks = objects.values_list('id', flat=True)
            ct = ContentType.objects.get_for_model(monitor_model)
            dataset = MonitorData.objects.filter(monitor=monitor, content_type=ct, object_id__in=pks)
        # Process dataset according to resource.period
        if resource.period == resource.MONTHLY_AVG:
            try:
                last = dataset.latest()
            except MonitorData.DoesNotExist:
                continue
            has_result = True
            epoch = datetime(year=today.year, month=today.month, day=1, tzinfo=timezone.utc)
            total = (last.created_at-epoch).total_seconds()
            dataset = dataset.filter(created_at__year=today.year, created_at__month=today.month)
            ini = epoch
            for data in dataset:
                slot = (data.created_at-ini).total_seconds()
                result += data.value * slot/total
                ini = data.created_at
        elif resource.period == resource.MONTHLY_SUM:
            dataset = dataset.filter(created_at__year=today.year, created_at__month=today.month)
            # FIXME Aggregation of 0s returns None! django bug?
            # value = dataset.aggregate(models.Sum('value'))['value__sum']
            values = dataset.values_list('value', flat=True)
            if values:
                has_result = True
                result += sum(values)
        elif resource.period == resource.LAST:
            try:
                result += dataset.latest().value
            except MonitorData.DoesNotExist:
                continue
            has_result = True
        else:
            raise NotImplementedError("%s support not implemented" % data.period)
    return result/resource.get_scale() if has_result else None
