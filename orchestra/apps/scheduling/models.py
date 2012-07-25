from celery.task.control import revoke
from common.collector import DependencyCollector, collect_related
from common.utils.models import generate_chainer_manager
from common.utils.python import _import
from common.utils.time import intersection, union, periods_intersection, periods_union, Period
from datetime import datetime
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
import settings
from tasks import schedule_deletion_task, schedule_deactivation_task


#TODO: this app is based on snapshot approach to make sure that we can retrieve the current state at some point on the future,
#      It would be nice if this behaviour is integrated on the create method but at the same time it is hard to implement
#      Advantage: 
#            1) performance, since there is no need to calculate on the fly the deletion_date or deactivation periods
#            2) consistency, since we guarantee that always is posible to know the state at any point on the past, 
#                            in the snapshot approach it's only possible when there is an snapshot available
#
#TODO  auto snapshot and manual snapshot on settings?
#TODO  union of overlaping periods by default? 


class DeletionDateQuerySet(models.query.QuerySet):
    def by_object(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return self.filter(object_id=obj.pk, content_type=ct)
    
    def active(self, *args, **kwargs):
        return self.filter(revoke_date__isnull=True).filter(*args, **kwargs)


class DeletionDate(models.Model):
    """ This model allows to schedule future deletions. Aditionally it keeps 
        track of every related object change (deletion dates and object relations) 
        in order to be able to retrieve the state of the system in any date on the past.
    """
    register_date = models.DateTimeField(auto_now_add=True)
    deletion_date = models.DateTimeField()
    revoke_date = models.DateTimeField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True)
    snapshot = models.BooleanField(default=False)
    
    content_object = generic.GenericForeignKey()
    objects = generate_chainer_manager(DeletionDateQuerySet)
    
    class Meta:
        ordering = ['-register_date']

    def __unicode__(self):
        return str(self.content_object)

    @classmethod
    def create(cls, obj, date, snapshot=False):
        ct = ContentType.objects.get_for_model(obj)
        deletion = cls.objects.create(content_type=ct, object_id=obj.pk, 
                                      deletion_date=date, snapshot=snapshot)
        deletion.save()
        if not snapshot:
            schedule_deletion_task.apply_async(args=[deletion.pk,], 
                                               eta=date, 
                                               task_id="deletion.%s" % deletion.pk)
        
    @classmethod
    def take_snapshot(cls, instances, related=False):
        """ Create snapshot of the instances for future reference of their current state 
            if related: all related instance too.
        """
        if not isinstance(instances, list):
            instances = [instances]
            
        if related:
            instances = collect_related(instances)

        for instance in instances:
            cancel_date = cls.lookup_cancel_date(instance)
            # Must be as much one active deletion date per snapshot            
            try: old_snap = cls.objects.by_object(instance).active().get(snapshot=True)
            except cls.DoesNotExist: old_snap = None
            if cancel_date and not old_snap:
                cls.create(instance, cancel_date, snapshot=True)
            elif cancel_date and cancel_date != old_snap:
                old_snap.revoke()
                cls.create(instance, cancel_date, snapshot=True)
            elif not cancel_date and old_snap:
                old_snap.revoke()
    
    def revoke(self):
        if not self.snapshot:
            revoke("deletion.%s" % self.pk)
        self.revoke_date = datetime.now()
        self.save()

    @classmethod
    def get(cls, obj):
        cd = cls.objects.by_object(obj).active().exclude(snapshot=True).order_by('deletion_date')
        return cd[0] if cd else None
        
    @classmethod
    def get_cancel_date(cls, obj):
        cd = cls.get(obj)
        return cd.deletion_date if cd else None

    @classmethod
    def lookup_cancel_date(cls, obj):
        return cls._lookup_cancel_date(DependencyCollector(obj).edge)
    
    @classmethod
    def _lookup_cancel_date(cls, node):
        cancel_date = cls.get_cancel_date(node.content)
        for parent in node.parents:
            if isinstance(parent, list):
                # AND case (MAX)
                current_cancel_date = cls._lookup_cancel_date(parent.pop())
                if current_cancel_date:
                    for and_parent in parent:
                        _cancel_date = cls._lookup_cancel_date(and_parent)
                        if not _cancel_date:
                            current_cancel_date = None
                            break
                        current_cancel_date = max(current_cancel_date, _cancel_date)
            else:
                # OR case (MIN)
                current_cancel_date = cls._lookup_cancel_date(parent)
            if current_cancel_date and (not cancel_date or current_cancel_date < cancel_date):
                cancel_date = current_cancel_date
        return cancel_date



class DeactivationPeriodQuerySet(models.query.QuerySet):
    def by_object(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return self.filter(object_id=obj.pk, content_type=ct)

    def active(self):
        return self.filter(revoke_date__isnull=True)


class DeactivationPeriod(models.Model):
    register_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    revoke_date = models.DateTimeField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True)
    snapshot = models.BooleanField(default=False)
    
    content_object = generic.GenericForeignKey()
    objects = generate_chainer_manager(DeactivationPeriodQuerySet)
    
    class Meta:
        ordering = ['-register_date']
        
    def __unicode__(self):
        return str(self.content_object)

    @classmethod
    def create(cls, obj, start_date, end_date, snapshot=False):
        ct = ContentType.objects.get_for_model(obj)
        deactivation = cls.objects.create(content_type=ct, object_id=obj.pk, 
                                          start_date=start_date, 
                                          end_date=end_date, snapshot=snapshot)
        deactivation.save()

        if not snapshot:
            schedule_deactivation_task.apply_async(args=[deactivation.pk,], 
                                                   eta=start_date, 
                                                   task_id="deactivation.%s" % deactivation.pk)
            if end_date:
                schedule_deactivation_task.apply_async(args=[deactivation.pk,], 
                                                       eta=end_date, 
                                                       task_id="reactivation.%s" % deactivation.pk)

    @classmethod
    def take_snapshot(cls, instances):
        """ Take snapshot of the instances for future reference of their current state """
        
        if not isinstance(instances, list):
            instances = [instances]
            
        if related:
            instances = collect_related(instances)

        for instance in instances:
            qset = cls.objects.by_object(instance).active()
            keep_pks = []
            for period in cls.lookup_deactivation_periods(instance):
                try: old_snap = qset.filter(start_date=period.start_date, 
                                            end_date=period.end_date).get(snapshot=True)
                except cls.DoesNotExist: old_snap = None
                if not old_snap:
                    cls.create(instance, period.start_date, period.end_date, snapshot=True)
                else: keep_pks.append(old_snap.pk)
            for snap in qset.filter(snapshot=True).exclude(pk__in=keep_pks):
                snap.revoke()
    
    def revoke(self):
        if not self.snapshot:
            revoke("deactivation.%s" % self.pk)
            revoke("reactivation.%s" % self.pk)
        self.revoke_date = datetime.now()
        self.save()        
    
    @classmethod
    def get_deactivation_periods(cls, obj, date):
        return cls.objects.by_object(obj).active().exclude(snapshot=True).exclude(end_date__lte=date)

    @classmethod
    def lookup_deactivation_periods(cls, obj, date=datetime.min):
        periods = cls._lookup_deactivation_periods(DependencyCollector(obj).edge, date)
        # Merge overlaping periods
        return periods_union(periods, periods)
    
    @classmethod
    def _lookup_deactivation_periods(cls, node, date):
        periods = cls.get_deactivation_periods(node.content, date)
        for parent in node.parents:
            if isinstance(parent, list):
                # AND case (Interesction)
                first = parent.pop()
                current_periods = list(cls._lookup_deactivation_periods(first, date))
                # We need to take into account if any AND dependency is going to be cancelled
                current_deletion = DeletionDate.lookup_cancel_date(first.content)
                if current_deletion: current_periods.append(Period(current_deletion, datetime.max)) 
                if current_periods:
                    for and_parent in parent:
                        parent_periods = list(cls._lookup_deactivation_periods(and_parent, date))
                        parent_deletion = DeletionDate.lookup_cancel_date(and_parent.content)
                        if parent_deletion: parent_periods.append(Period(parent_deletion, datetime.max))
                        current_periods = periods_intersection(parent_periods, current_periods)
                        if not current_periods:
                            break
                    # Filter deletions
                    current_periods = filter(lambda period: period.end_date != datetime.max, current_periods)
                    
            else:
                # OR case (Union)
                current_periods = cls._lookup_deactivation_periods(parent, date)
            periods = periods_union(current_periods, periods)
        return periods


@property
def deactivation_periods(self):
    return DeactivationPeriod.lookup_deactivation_periods(self, date=datetime.now())

@property
def cancel_date(self):
    return DeletionDate.lookup_cancel_date(self)    

def set_cancel_date(self, date):
    DeletionDate.create(self, date)

def set_deactivation_period(self, start_date, end_date):
    DeactivationPeriod.create(self, start_date, end_date)

def revoke_deletions(self):
    pass

@property
def active(self):
    periods = list(self.deactivation_periods)
    now = datetime.now()
    if periods:
        for period in periods:
            if period.start_date < now:
                return False
    return True


for module in settings.SCHEDULING_SCHEDULABLE_MODELS:
    try: model = _import(module)
    except ImportError: continue
    model.cancel_date = cancel_date
    model.deactivation_periods = deactivation_periods
    model.set_cancel_date = set_cancel_date
    model.set_deactivation_period = set_deactivation_period
    model.active = active
