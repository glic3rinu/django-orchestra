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
    
    def compute_historic_usage(self, dataset):
        """ generates [(data, usage),] tuples for resource data history reporting """
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
    
    def monthly_historic_filter(self, dataset):
        today = timezone.now().date()
        date = datetime.date(
            year=today.year,
            month=today.month,
            day=1,
        )
        while True:
            dataset_copy = copy.copy(dataset)
            dataset_copy = self.filter(dataset_copy, date=date)
            try:
                dataset_copy[0]
            except IndexError:
                yield (date, None)
            yield (date, dataset_copy)
            date -= relativedelta(months=1)
    
    def historic_filter(self, dataset):
        yield (timezone.now().date(), self.filter(dataset))
        yield from self.monthly_historic_filter(dataset)
    
    def compute_usage(self, dataset):
        values = dataset.values_list('value', flat=True)
        if values:
            return sum(values)
        return None
    
    def compute_historic_usage(self, dataset):
        dataset = dataset.only('object_id', 'value', 'content_object_repr')
        return [(mdata, mdata.value) for mdata in dataset]


class MonthlySum(Last):
    """ Monthly sum the values of all monitors """
    name = 'monthly-sum'
    verbose_name = _("Monthly Sum")
    
    def filter(self, dataset, date=None):
        if date is None:
            date = timezone.now().date()
        return dataset.filter(
            created_at__year=date.year,
            created_at__month=date.month,
        )
    
    def historic_filter(self, dataset):
        yield from self.monthly_historic_filter(dataset)
    
    def compute_historic_usage(self, dataset):
        objects = {}
        mdatas = {}
        for mdata in dataset.only('object_id', 'value', 'content_object_repr'):
            mdatas[mdata.object_id] = mdata
            try:
                objects[mdata.object_id] += mdata.value
            except KeyError:
                objects[mdata.object_id] = mdata.value
        return [(mdatas[object_id], value) for object_id, value in objects.items()]


class MonthlyAvg(MonthlySum):
    """ sum of the monthly averages of each monitor """
    name = 'monthly-avg'
    verbose_name = _("Monthly AVG")
    
    def get_epoch(self, date=None):
        if date is None:
            date = timezone.now().date()
        return datetime.date(
            year=date.year,
            month=date.month,
            day=1,
        )
    
    def compute_usage(self, dataset, historic=False):
        result = 0
        has_result = False
        aggregate = []
        for object_id, dataset in dataset.order_by('created_at').group_by('object_id').items():
            try:
                last = dataset[-1]
            except IndexError:
                continue
            epoch = self.get_epoch(date=last.created_at)
            total = (last.created_at-epoch).total_seconds()
            ini = epoch
            current = 0
            for mdata in dataset:
                has_result = True
                slot = (mdata.created_at-ini).total_seconds()
                current += mdata.value * decimal.Decimal(str(slot/total))
                ini = mdata.created_at
            if historic:
                aggregate.append(
                    (mdata, current)
                )
            else:
                result += current
        if has_result:
            if historic:
                return aggregate
            return result
        return None
    
    def compute_historic_usage(self, dataset):
        return self.compute_usage(dataset, historic=True)


class Last10DaysAvg(MonthlyAvg):
    """ sum of the last 10 days averages of each monitor """
    name = 'last-10-days-avg'
    verbose_name = _("Last 10 days AVG")
    days = 10
    
    def get_epoch(self, date=None):
        if date is None:
            date = timezone.now().date()
        return date - datetime.timedelta(days=self.days)
    
    def filter(self, dataset, date=None):
        epoch = self.get_epoch(date=date)
        dataset = dataset.filter(created_at__gt=epoch)
        if date is not None:
            dataset = dataset.filter(created_at__lte=date)
        return dataset
    
    def historic_filter(self, dataset):
        yield (timezone.now().date(), self.filter(dataset))
        yield from super(Last10DaysAvg, self).historic_filter(dataset)
