from django.template.defaultfilters import date as date_filter


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
                'dates': set(),
                'objects': [],
            }
            resources[resource] = (options, aggregation)
        
        monitors = []
        scale = options['scale']
        all_dates = options['dates']
        for monitor_name, dataset in rdata.get_monitor_datasets():
            datasets = {}
            for content_object, datas in aggregation.aggregate_history(dataset):
                if aggregation.aggregated_history:
                    needs_aggregation = True
                    serie = {}
                    for data in datas:
                        date = date_filter(data.date)
                        value = round(float(data.value or 0)/scale, 2)
                        all_dates.add(date)
                        serie[date] = value
                else:
                    serie = []
                    for data in datas:
                        date = data.created_at.timestamp()
                        date = int(str(date).split('.')[0] + '000')
                        value = round(float(data.value or 0)/scale, 2)
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
            'current': round(float(rdata.used), 3),
            'allocated': float(rdata.allocated) if rdata.allocated is not None else None,
            'updated_at': rdata.updated_at.isoformat(),
            'monitors': monitors,
        })
    if needs_aggregation:
        result = []
        for options, aggregation in resources.values():
            if aggregation.aggregated_history:
                all_dates = options['dates']
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
