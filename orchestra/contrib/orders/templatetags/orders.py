import datetime

from django import template
from django.template.defaultfilters import date


register = template.Library()


@register.filter
def periodformat(line):
    if line.ini == line.end:
        return date(line.ini)
    if line.ini.day == 1 and line.end.day == 1:
        end = line.end - datetime.timedelta(days=1)
        if line.ini.month == end.month:
            return date(line.ini, "N Y")
        return '%s to %s' % (date(line.ini, "N Y"), date(end, "N Y"))
    return '%s to %s' % (date(line.ini), date(line.end))
