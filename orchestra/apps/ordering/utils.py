from datetime import datetime
from mx.DateTime import DateTime, RelativeDateTime
import settings


class p_dict(dict):
    all_values = []
    

class Period(object):
    ini = None
    end = None
    
    def __init__(self, ini, end):
        super(Period, self).__init__()
        self.ini = ini
        self.end = end
        
    def __unicode__(self):
        return "%s - %s" % (self.ini, self.end)    


def get_relative_period(period):
    return RelativeDateTime(months=period)
    
    
def renew_month(period):
    if period == settings.MONTHLY: return 1
    if period == settings.ANUAL: return settings.ANUAL_RENEW_MONTH
    if period == settings.SIX_MONTHS: return settings.SIX_MONTHS_RENEW_MONTH
    if period == settings.FOUR_MONTHS: return settings.FOUR_MONTHS_RENEW_MONTH
    if period == settings.THREE_MONTHS: return settings.THREE_MONTHS_RENEW_MONTH
    if period == settings.TWO_MONTHS: return settings.TWO_MONTHS_RENEW_MONTH


def DateTime_conv(date):
    return DateTime(date.year, date.month, date.day, date.hour, date.minute, date.second+1e-6*date.microsecond)


def get_next_point(period, fixed, date, var_point=None):
    """ date is the point for variable periods. Returns a DateTime and RelativeDateTime """ 
    if type(date) != type(DateTime(2000)):
        date = DateTime_conv(date)
        
    incremental = get_relative_period(period)
    if fixed:   
        year = date.year
        month = date.month
        current_month = DateTime(year, month, 1)
        initial = DateTime(year, renew_month(period), 1)

        while initial <= current_month:
            initial += incremental            
    else:
        if not var_point: initial = date
        else: initial = DateTime_conv(var_point)
        while initial <= date:
            initial += incremental
    return initial, incremental


def get_prev_point(period, fixed, date, var_point=None):
    next, increment = get_next_point(period, fixed, date, var_point)
    prev = next - increment
    return prev, increment


