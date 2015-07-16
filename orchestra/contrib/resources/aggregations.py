import copy
import datetime
import decimal

from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra import plugins


class Aggregation(plugins.Plugin, metaclass=plugins.PluginMount):
    """ filters and computes dataset usage """
    def filter(self, dataset):
        """ Filter the dataset to get the relevant data according to the period """
        raise NotImplementedError
    
    def historic_filter(self, dataset):
        """ Generates (date, dataset) tuples for resource data history reporting """
        raise NotImplementedError
    
    def compute_usage(self, dataset):
        """ given a dataset computes its usage according to the method (avg, sum, ...) """
        raise NotImplementedError


class Last(Aggregation):
    """ Sum of the last value of all monitors """
    name = 'last'
    verbose_name = _("Last value")
    
    def filter(self, dataset, date=None):
        dataset = dataset.order_by('object_id', '-id').distinct('monitor')
        if date is not None:
            dataset = dataset.filter(created_at__lte=date)
        return dataset
    
    def historic_filter(self, dataset):
        yield (timezone.now(), self.filter(dataset))
        now = timezone.now()
        date = datetime.datetime(
            year=now.year,
            month=now.month,
            day=1,
            tzinfo=timezone.utc,
        )
        while True:
            dataset_copy = copy.copy(dataset)
            dataset_copy = self.filter(dataset_copy, date=date)
            try:
                dataset_copy[0]
            except IndexError:
                raise StopIteration
            yield (date, dataset_copy)
            date -= relativedelta(months=1)
    
    def compute_usage(self, dataset):
        values = dataset.values_list('value', flat=True)
        if values:
            return sum(values)
        return None


class MonthlySum(Last):
    """ Monthly sum the values of all monitors """
    name = 'monthly-sum'
    verbose_name = _("Monthly Sum")
    
    def filter(self, dataset, date=None):
        if date is None:
            date = timezone.now()
        return dataset.filter(
            created_at__year=date.year,
            created_at__month=date.month,
        )
    
    def historic_filter(self, dataset):
        now = timezone.now()
        date = datetime.datetime(
            year=now.year,
            month=now.month,
            day=1,
            tzinfo=timezone.utc,
        )
        while True:
            dataset_copy = copy.copy(dataset)
            dataset_copy = self.filter(dataset_copy, date=date)
            try:
                dataset_copy[0]
            except IndexError:
                raise StopIteration
            yield (date, dataset_copy)
            date -= relativedelta(months=1)


class MonthlyAvg(MonthlySum):
    """ sum of the monthly averages of each monitor """
    name = 'monthly-avg'
    verbose_name = _("Monthly AVG")
    
    def filter(self, dataset, date=None):
        qs = super(MonthlyAvg, self).filter(dataset, date=date)
        return qs.order_by('created_at')
    
    def get_epoch(self, date=None):
        if date is None:
            date = timezone.now()
        return datetime.datetime(
            year=date.year,
            month=date.month,
            day=1,
            tzinfo=timezone.utc,
        )
    
    def compute_usage(self, dataset):
        result = 0
        has_result = False
        for monitor, dataset in dataset.group_by('monitor').items():
            try:
                last = dataset[-1]
            except IndexError:
                continue
            epoch = self.get_epoch(date=last.created_at)
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
    
    def get_epoch(self, date=None):
        if date is None:
            date = timezone.now()
        return date - datetime.timedelta(days=self.days)
    
    def filter(self, dataset, date=None):
        epoch = self.get_epoch(date=date)
        dataset = dataset.filter(created_at__gt=epoch).order_by('created_at')
        if date is not None:
            dataset = dataset.filter(created_at__lte=date)
        return dataset
    
    def historic_filter(self, dataset):
        yield (timezone.now(), self.filter(dataset))
        yield from super(Last10DaysAvg, self).historic_filter(dataset)
