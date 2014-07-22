from datetime import datetime

from django.utils import timezone
from django.utils.translation import ungettext, ugettext as _


def pluralize_year(n):
    return ungettext(_('{num:.1f} year ago'), _('{num:.1f} years ago'), n)


def pluralize_month(n):
    return ungettext(_('{num:.1f} month ago'), _('{num:.1f} months ago'), n)


def pluralize_week(n):
    return ungettext(_('{num:.1f} week ago'), _('{num:.1f} weeks ago'), n)


def pluralize_day(n):
    return ungettext(_('{num:.1f} day ago'), _('{num:.1f} days ago'), n)


OLDER_CHUNKS = (
    (365.0, pluralize_year),
    (30.0, pluralize_month),
    (7.0, pluralize_week),
)


def _un(singular__plural, n=None):
    singular, plural = singular__plural
    return ungettext(singular, plural, n)


def naturaldate(date, include_seconds=False):
    """Convert datetime into a human natural date string."""
    if not date:
        return ''
    
    right_now = timezone.now()
    today = datetime(right_now.year, right_now.month,
                     right_now.day, tzinfo=right_now.tzinfo)
    delta = right_now - date
    delta_midnight = today - date
    
    days = delta.days
    hours = int(round(delta.seconds / 3600, 0))
    minutes = delta.seconds / 60
    seconds = delta.seconds
    
    if days < 0:
        return _('just now')
    
    if days == 0:
        if hours == 0:
            if minutes > 0:
                minutes += float(seconds)/60
                return ungettext(
                    _('{minutes:.1f} minute ago'),
                    _('{minutes:.1f} minutes ago'), minutes
                ).format(minutes=minutes)
            else:
                if include_seconds and seconds:
                    return ungettext(
                        _('{seconds} second ago'),
                        _('{seconds} seconds ago'), seconds
                    ).format(seconds=seconds)
                return _('just now')
        else:
            hours += float(minutes)/60
            return ungettext(
                _('{hours:.1f} hour ago'), _('{hours:.1f} hours ago'), hours
            ).format(hours=hours)
    
    if delta_midnight.days == 0:
        return _('yesterday at {time}').format(time=date.strftime('%H:%M'))
    
    count = 0
    for chunk, pluralizefun in OLDER_CHUNKS:
        if days < 7.0:
            count = days + float(hours)/24
            fmt = pluralize_day(count)
            return fmt.format(num=count)
        if days >= chunk:
            count = (delta_midnight.days + 1) / chunk
            fmt = pluralizefun(count)
            return fmt.format(num=count)
