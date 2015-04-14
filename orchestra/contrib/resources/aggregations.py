import datetime
import decimal

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra import plugins


class Aggregation(plugins.Plugin, metaclass=plugins.PluginMount):
    """ filters and computes dataset usage """
    def filter(self, dataset):
        """ Filter the dataset to get the relevant data according to the period """
        raise NotImplementedError
    
    def compute_usage(self, dataset):
        """ given a dataset computes its usage according to the method (avg, sum, ...) """
        raise NotImplementedError


class Last(Aggregation):
    """ Sum of the last value of all monitors """
    name = 'last'
    verbose_name = _("Last value")
    
    def filter(self, dataset):
        try:
            return dataset.order_by('object_id', '-id').distinct('monitor')
        except dataset.model.DoesNotExist:
            return dataset.none()
    
    def compute_usage(self, dataset):
        values = dataset.values_list('value', flat=True)
        if values:
            return sum(values)
        return None


class MonthlySum(Last):
    """ Monthly sum the values of all monitors """
    name = 'monthly-sum'
    verbose_name = _("Monthly Sum")
    
    def filter(self, dataset):
        today = timezone.now()
        return dataset.filter(
            created_at__year=today.year,
            created_at__month=today.month
        )


class MonthlyAvg(MonthlySum):
    """ sum of the monthly averages of each monitor """
    name = 'monthly-avg'
    verbose_name = _("Monthly AVG")
    
    def filter(self, dataset):
        qs = super(MonthlyAvg, self).filter(dataset)
        return qs.order_by('created_at')
    
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
        has_result = False
        for monitor, dataset in dataset.group_by('monitor').items():
            try:
                last = dataset[-1]
            except IndexError:
                continue
            epoch = self.get_epoch()
            total = (last.created_at-epoch).total_seconds()
            ini = epoch
            for data in dataset:
                has_result = True
                slot = (data.created_at-ini).total_seconds()
                result += data.value * decimal.Decimal(str(slot/total))
                ini = data.created_at
        if has_result:
            return result
        return None


class Last10DaysAvg(MonthlyAvg):
    """ sum of the last 10 days averages of each monitor """
    name = 'last-10-days-avg'
    verbose_name = _("Last 10 days AVG")
    days = 10
    
    def get_epoch(self):
        today = timezone.now()
        return today - datetime.timedelta(days=self.days)
    
    def filter(self, dataset):
        epoch = self.get_epoch()
        return dataset.filter(created_at__gt=epoch).order_by('created_at')
