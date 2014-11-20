import datetime


def compute_resource_usage(data):
    """ Computes MonitorData.used based on related monitors """
    resource = data.resource
    result = 0
    has_result = False
    for dataset in data.get_monitor_datasets():
        if resource.period == resource.MONTHLY_AVG:
            last = dataset.latest()
            epoch = datetime(
                year=today.year,
                month=today.month,
                day=1,
                tzinfo=timezone.utc
            )
            total = (last.created_at-epoch).total_seconds()
            ini = epoch
            for data in dataset:
                slot = (data.created_at-ini).total_seconds()
                result += data.value * slot/total
                ini = data.created_at
        elif resource.period == resource.MONTHLY_SUM:
            # FIXME Aggregation of 0s returns None! django bug?
            # value = dataset.aggregate(models.Sum('value'))['value__sum']
            values = dataset.values_list('value', flat=True)
            if values:
                has_result = True
                result += sum(values)
        elif resource.period == resource.LAST:
            result += dataset.value
            has_result = True
        else:
            raise NotImplementedError("%s support not implemented" % data.period)
    return float(result)/resource.get_scale() if has_result else None
