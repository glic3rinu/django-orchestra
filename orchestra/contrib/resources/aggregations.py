import datetime
import decimal
import itertools

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.utils.python import AttrDict

from orchestra import plugins


class Aggregation(plugins.Plugin, metaclass=plugins.PluginMount):
    """ filters and computes dataset usage """
    aggregated_history = False
    
    def filter(self, dataset):
        """ Filter the dataset to get the relevant data according to the period """
        raise NotImplementedError
    
    def compute_usage(self, dataset):
        """ given a dataset computes its usage according to the method (avg, sum, ...) """
        raise NotImplementedError
    
    def aggregate_history(self, dataset):
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
    
    def compute_usage(self, dataset):
        values = dataset.values_list('value', flat=True)
        if values:
            return sum(values)
        return None
    
    def aggregate_history(self, dataset):
        prev_object_id = None
        prev_object_repr = None
        for mdata in dataset.order_by('object_id', 'created_at'):
            object_id = mdata.object_id
            if object_id != prev_object_id:
                if prev_object_id is not None:
                    yield (prev_object_repr, datas)
                datas = [mdata]
            else:
                datas.append(mdata)
            prev_object_id = object_id
            prev_object_repr = mdata.content_object_repr
        if prev_object_id is not None:
            yield (prev_object_repr, datas)


class MonthlySum(Last):
    """ Monthly sum the values of all monitors """
    name = 'monthly-sum'
    verbose_name = _("Monthly Sum")
    aggregated_history = True
    
    def filter(self, dataset, date=None):
        if date is None:
            date = timezone.now().date()
        return dataset.filter(
            created_at__year=date.year,
            created_at__month=date.month,
        )
    
    def aggregate_history(self, dataset):
        prev = None
        prev_object_id = None
        datas = []
        sink = AttrDict(object_id=-1, value=-1, content_object_repr='',
            created_at=AttrDict(year=-1, month=-1))
        for mdata in itertools.chain(dataset.order_by('object_id', 'created_at'), [sink]):
            object_id = mdata.object_id
            ymonth = (mdata.created_at.year, mdata.created_at.month)
            if object_id != prev_object_id or ymonth != prev.ymonth:
                if prev_object_id is not None:
                    data = AttrDict(
                        date=datetime.date(
                            year=prev.ymonth[0],
                            month=prev.ymonth[1],
                            day=1
                        ),
                        value=current,
                        content_object_repr=prev.content_object_repr
                    )
                    datas.append(data)
                current = mdata.value
            else:
                current += mdata.value
            if object_id != prev_object_id:
                if prev_object_id is not None:
                    yield (prev.content_object_repr, datas)
                    datas = []
            prev = mdata
            prev.ymonth = ymonth
            prev_object_id = object_id


class MonthlyAvg(MonthlySum):
    """ sum of the monthly averages of each monitor """
    name = 'monthly-avg'
    verbose_name = _("Monthly AVG")
    aggregated_history = False
    
    def get_epoch(self, date=None):
        if date is None:
            date = timezone.now().date()
        return datetime.date(
            year=date.year,
            month=date.month,
            day=1,
        )
    
    def compute_usage(self, dataset):
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
            else:
                result += current
        if has_result:
            return result
        return None
    
    def aggregate_history(self, dataset):
        yield from super(MonthlySum, self).aggregate_history(dataset)


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
