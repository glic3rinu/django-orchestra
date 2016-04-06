from datetime import datetime

from django.utils import timezone
from django.utils.translation import ungettext, ugettext as _


def verbose_time(n, units, ago='ago'):
    if n >= 5:
        return _("{n} {units} {ago}").format(n=int(n), units=units, ago=ago)
    return ungettext(
        _("{n:.1f} {s_units} {ago}"),
        _("{n:.1f} {units} {ago}"), n
    ).format(n=n, units=units, s_units=units[:-1], ago=ago)


OLDER_CHUNKS = (
    (365.0, 'years'),
    (30.0, 'months'),
    (7.0, 'weeks'),
)


def _un(singular__plural, n=None):
    singular, plural = singular__plural
    return ungettext(singular, plural, n)


def naturaldatetime(date, show_seconds=False):
    """Convert datetime into a human natural date string."""
    if not date:
        return ''
    
    right_now = timezone.now()
    today = datetime(right_now.year, right_now.month,
                     right_now.day, tzinfo=right_now.tzinfo)
    delta = right_now - date
    delta_midnight = today - date
    
    days = delta.days
    hours = float(delta.seconds) / 3600
    minutes = float(delta.seconds) / 60
    seconds = delta.seconds
    
    days = abs(days)
    ago = ''
    if right_now > date:
        ago = 'ago'
    
    if days == 0:
        if int(hours) == 0:
            if minutes >= 1 or not show_seconds:
                return verbose_time(minutes, 'minutes', ago=ago)
            else:
                return verbose_time(seconds, 'seconds', ago=ago)
        else:
            return verbose_time(hours, 'hours', ago=ago)
    
    if delta_midnight.days == 0:
        date = timezone.localtime(date)
        return _("yesterday at {time}").format(time=date.strftime('%H:%M'))
    
    count = 0
    for chunk, units in OLDER_CHUNKS:
        if days < 7.0:
            count = days + float(hours)/24
            return verbose_time(count, 'days', ago=ago)
        if days >= chunk:
            count = (delta_midnight.days + 1) / chunk
            count = abs(count)
            return verbose_time(count, units, ago=ago)


def naturaldate(date):
    if not date:
        return ''
    
    today = timezone.now().date()
    delta = today - date
    days = delta.days
    
    if days == 0:
        return _('today')
    elif days == 1:
        return _('yesterday')
    ago = ' ago'
    if days < 0 or today < date:
        ago = ''
    days = abs(days)
    delta_midnight = today - date
    
    count = 0
    for chunk, units in OLDER_CHUNKS:
        if days < 7.0:
            count = days
            fmt = verbose_time(count, 'days', ago=ago)
            return fmt.format(num=count, ago=ago)
        if days >= chunk:
            count = (delta_midnight.days + 1) / chunk
            count = abs(count)
            fmt = verbose_time(count, units, ago=ago)
            return fmt.format(num=count, ago=ago)


def text2int(textnum, numwords={}):
    if not numwords:
        units = (
            'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
            'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',
            'sixteen', 'seventeen', 'eighteen', 'nineteen',
        )
        
        tens = ('', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety')
        
        scales = ['hundred', 'thousand', 'million', 'billion', 'trillion']
        
        numwords['and'] = (1, 0)
        for idx, word in enumerate(units):
            numwords[word] = (1, idx)
        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):
            numwords[word] = (10 ** (idx * 3 or 2), 0)
    
    current = result = 0
    for word in textnum.split():
        word = word.lower()
        if word not in numwords:
          raise Exception("Illegal word: " + word)
        
        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0
    
    return result + current


UNITS_CONVERSIONS = {
    1024**4: ['TB', 'TiB', 'TERABYTES'],
    1024**3: ['GB', 'GiB', 'GYGABYTES'],
    1024**2: ['MB', 'MiB', 'MEGABYTES'],
    1024: ['KB', 'KiB', 'KYLOBYTES'],
    1: ['B', 'BYTES'],
}

def unit_to_bytes(unit):
    for bytes, units in UNITS_CONVERSIONS.items():
        if unit in units:
            return bytes
    raise KeyError("%s is not a valid unit." % unit)
