from datetime import datetime
from resources import settings


def split_period(period):
    """ Return the intial, end for the period related to now() """ 
    now = datetime.now()
    year = now.year
    if period == settings.ANUAL:
        return datetime(year=year, month=1, day=1), now
        
    month = now.month
    if period == settings.MONTHLY:
        return datetime(year=year, month=month, day=1), now
        
    day = now.day
    if period == settings.DAILY:
        return datetime(year=year, month=month, day=day), now 
        
    else: 
        raise "Unknown period"


