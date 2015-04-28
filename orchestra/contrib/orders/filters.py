from datetime import timedelta, datetime

from django.contrib.admin import SimpleListFilter
from django.db.models import Q, Prefetch, F
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from .models import MetricStorage, Order


class ActiveOrderListFilter(SimpleListFilter):
    """ Filter tickets by created_by according to request.user """
    title = _("is active")
    parameter_name = 'is_active'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("Active")),
            ('False', _("Inactive")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.active()
        elif self.value() == 'False':
            return queryset.inactive()
        return queryset


class BilledOrderListFilter(SimpleListFilter):
    """ Filter tickets by created_by according to request.user """
    title = _("billed")
    parameter_name = 'billed'
#    apply_last = True
    
    def lookups(self, request, model_admin):
        return (
            ('yes', _("Billed")),
            ('no', _("Not billed")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(billed_until__isnull=False, billed_until__gte=timezone.now())
        elif self.value() == 'no':
            mindelta = timedelta(days=2) # TODO
            metric_pks = []
            prefetch_valid_metrics = Prefetch('metrics', to_attr='valid_metrics',
                queryset=MetricStorage.objects.filter(created_on__gt=F('order__billed_on'),
                    created_on__lte=(F('updated_on')-mindelta))
            )
            prefetch_billed_metric = Prefetch('metrics', to_attr='billed_metric',
                queryset=MetricStorage.objects.filter(order__billed_on__isnull=False,
                    created_on__lte=F('order__billed_on'), updated_on__gt=F('order__billed_on'))
            )
            metric_queryset = queryset.exclude(service__metric='').exclude(billed_on__isnull=True)
            for order in metric_queryset.prefetch_related(prefetch_valid_metrics, prefetch_billed_metric):
                if len(order.billed_metric) != 1:
                    raise ValueError("Data inconsistency.")
                billed_metric = order.billed_metric[0].value
                for metric in order.valid_metrics:
                    if metric.created_on <= order.billed_on:
                        raise ValueError("This value should already be filtered on the prefetch query.")
                    if metric.value > billed_metric:
                        metric_pks.append(order.pk)
                        break
            return queryset.filter(
                Q(pk__in=metric_pks) | Q(
                    Q(billed_until__isnull=True) | Q(billed_until__lt=timezone.now())
                )
            )
        return queryset


class IgnoreOrderListFilter(SimpleListFilter):
    """ Filter Nodes by group according to request.user """
    title = _("Ignore")
    parameter_name = 'ignore'
    
    def lookups(self, request, model_admin):
        return (
            ('0', _("Not ignored")),
            ('1', _("Ignored")),
            ('2', _("All")),
            
        )
    
    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(ignore=False)
        elif self.value() == '1':
            return queryset.filter(ignore=True)
        return queryset
    
    def choices(self, cl):
        """ Enable default selection different than All """
        for lookup, title in self.lookup_choices:
            title = title._proxy____args[0]
            selected = self.value() == force_text(lookup)
            if not selected and title == "Not ignored" and self.value() is None:
                selected = True
            # end of workaround
            yield {
                'selected': selected,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }
