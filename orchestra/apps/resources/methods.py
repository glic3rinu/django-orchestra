import datetime
import decimal

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra import plugins


class DataMethod(plugins.Plugin, metaclass=plugins.PluginMount):
    """ filters and computes dataset usage """
    def filter(self, dataset):
        """ Filter the dataset to get the relevant data according to the period """
        raise NotImplementedError
    
    def compute_usage(self, dataset):
        """ given a dataset computes its usage according to the method (avg, sum, ...) """
        raise NotImplementedError


class Last(DataMethod):
    name = 'last'
    verbose_name = _("Last value")
    
    def filter(self, dataset):
        try:
            return dataset.order_by('object_id', '-id').distinct('object_id')
        except dataset.model.DoesNotExist:
            return dataset.none()
    
    def compute_usage(self, dataset):
        # FIXME Aggregation of 0s returns None! django bug?
        #       value = dataset.aggregate(models.Sum('value'))['value__sum']
        values = dataset.values_list('value', flat=True)
        if values:
            return sum(values)
        return None


class MonthlySum(Last):
    name = 'monthly-sum'
    verbose_name = _("Monthly Sum")
    
    def filter(self, dataset):
        today = timezone.now()
        return dataset.filter(
            created_at__year=today.year,
            created_at__month=today.month
        )


class MonthlyAvg(MonthlySum):
    name = 'monthly-avg'
    verbose_name = _("Monthly AVG")
    
    def get_epoch(self):
        today = timezone.now()
        return datetime(
            year=today.year,
            month=today.month,
            day=1,
            tzinfo=timezone.utc
        )
    
    def compute_usage(self, dataset):
        result = 0
        try:
            last = dataset.latest()
        except dataset.model.DoesNotExist:
            return result
        epoch = self.get_epoch()
        total = (last.created_at-epoch).total_seconds()
        ini = epoch
        for data in dataset:
            slot = (data.created_at-ini).total_seconds()
            result += data.value * decimal.Decimal(str(slot/total))
            ini = data.created_at
        return result


class Last10DaysAvg(MonthlyAvg):
    name = 'last-10-days-avg'
    verbose_name = _("Last 10 days AVG")
    days = 10
    
    def get_epoch(self):
        today = timezone.now()
        return today - datetime.timedelta(days=self.days)
    
    def filter(self, dataset):
        return dataset.filter(created_at__gt=self.get_epoch())
