import decimal

from django.template.defaultfilters import date as date_format


def get_history_data(queryset):
    resources = {}
    needs_aggregation = False
    for rdata in queryset:
        resource = rdata.resource
        try:
            (options, aggregation) = resources[resource]
        except KeyError:
            aggregation = resource.aggregation_instance
            options = {
                'aggregation': str(aggregation.verbose_name),
                'aggregated_history': aggregation.aggregated_history,
                'content_type': rdata.content_type.model,
                'content_object': rdata.content_object_repr,
                'unit': resource.unit,
                'scale': resource.get_scale(),
                'verbose_name': str(resource.verbose_name),
                'dates': set() if aggregation.aggregated_history else None,
                'objects': [],
            }
            resources[resource] = (options, aggregation)
        if aggregation.aggregated_history:
            needs_aggregation = True
        monitors = []
        scale = options['scale']
        all_dates = options['dates']
        for monitor_name, dataset in rdata.get_monitor_datasets():
            datasets = {}
            for content_object, datas in aggregation.aggregate_history(dataset):
                if aggregation.aggregated_history:
                    serie = {}
                    for data in datas:
                        value = round(float(data.value)/scale, 3) if data.value is not None else None
                        all_dates.add(data.date)
                        serie[data.date] = value
                else:
                    serie = []
                    for data in datas:
                        date = data.created_at.timestamp()
                        date = int(str(date).split('.')[0] + '000')
                        value = round(float(data.value)/scale, 3) if data.value is not None else None
                        serie.append(
                            (date, value)
                        )
                datasets[content_object] = serie
            monitors.append({
                'name': monitor_name,
                'datasets': datasets,
            })
        options['objects'].append({
            'object_name': rdata.content_object_repr,
            'current': round(float(rdata.used or 0), 3),
            'allocated': float(rdata.allocated) if rdata.allocated is not None else None,
            'updated_at': rdata.updated_at.isoformat() if rdata.updated_at else None,
            'monitors': monitors,
        })
    if needs_aggregation:
        result = []
        for options, aggregation in resources.values():
            if aggregation.aggregated_history:
                all_dates = sorted(options['dates'])
                options['dates'] = [date_format(date) for date in all_dates]
                for obj in options['objects']:
                    for monitor in obj['monitors']:
                        series = []
                        for content_object, dataset in monitor['datasets'].items():
                            data = []
                            for date in all_dates:
                                data.append(dataset.get(date, 0.0))
                            series.append({
                                'name': content_object,
                                'data': data,
                            })
                        monitor['datasets'] = series
            result.append(options)
    else:
        result = [resource[0] for resource in resources.values()]
    return result


def delete_old_equal_values(dataset):
    """ only first and last values of an equal serie (+-error) are kept """
    prev_value = None
    prev_key = None
    delete_count = 0
    error = decimal.Decimal('0.005')
    third = False
    for mdata in dataset.order_by('content_type_id', 'object_id', 'created_at'):
        key = (mdata.content_type_id, mdata.object_id)
        if prev_key == key:
            if prev_value is not None and mdata.value*(1-error) < prev_value < mdata.value*(1+error):
                if third:
                    prev.delete()
                    delete_count += 1
                else:
                    third = True
            else:
                third = False
            prev_value = mdata.value
            prev_key = key
        else:
            prev_value = None
            prev_key = key
        prev = mdata
    return delete_count


def monthly_sum_old_values(dataset):
    aggregated = 0
    prev_key = None
    prev = None
    to_delete = []
    delete_count = 0
    for mdata in dataset.order_by('content_type_id', 'object_id', 'created_at'):
        key = (mdata.content_type_id, mdata.object_id, mdata.created_at.year, mdata.created_at.month)
        if prev_key is not None and prev_key != key:
            if prev.value != aggregated:
                prev.value = aggregated
                prev.save(update_fields=('value',))
            for obj in to_delete[:-1]:
                obj.delete()
                delete_count += 1
            aggregated = 0
            to_delete = []
        prev = mdata
        prev_key = key
        aggregated += mdata.value
        to_delete.append(mdata)
    return delete_count
