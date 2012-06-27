from datetime import datetime
from scheduling.models import DeletionDate, DeactivationPeriod


def active_cancellations(obj, ini=datetime.min, end=datetime.max):
    """ Return cancellation dates active during lt and gt dates """
    DeletionDate.objects.by_object(obj).active(deletion_date__lt=end, deletion_date__gt=ini)
    

def registred_cancellations(obj, ini=datetime.min, end=datetime.max):
    """ Return cancellation dates registred between lt and gt dates """
    DeletionDate.objects.by_object(obj).filter(register_date__lt=end, register_date__gt=ini)

    
def annulated_cancellations(obj, ini=datetime.min, end=datetime.max):
    """ Return cancellation dates annulated between lt and gt dates""""
    DeletionDate.objects.by_object(obj).filter(revoke_date__lt=end, revoke_date__gt=ini)


def active_deactivations(obj, ini=datetime.min, end=datetime.max):
    """ Return deactivation periods active during lt and gt dates """
    DeactivationPeriod.by_object(obj).active(start_date__lt=end, end_date__gt=ini)

  
def registred_deactivations(obj, ini=datetime.min, end=datetime.max):
    """ Return deactivation periods registred between lt and gt dates """
    DeactivationPeriod.by_object(obj).filter(register_date__lt=end, register_date__gt=ini)
    
    
def annulated_deactivations(obj, ini=datetime.min, end=datetime.max):
    """ Return deactivation periods annulated between lt and gt dates """
    DeactivationPeriod.objects.by_object(obj).filter(revoke_date__end=end, revoke_date__gt=ini)
