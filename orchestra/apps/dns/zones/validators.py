import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_zone_interval(value):
    msg = _("%s is not an appropiate zone interval value") % value
    if value[-1] not in ('s', 'm', 'h', 'd', 'w') and not value[-1].isdigit():
        raise ValidationError(msg)
    try:
        int(value[:-1])
    except ValueError:
        raise ValidationError(msg)


def validate_zone_serial(value):
    if len(str(value)) != 10:
        raise ValidationError(_("%s is not an appropiate zone serial number") % value)


def validate_zone_label(value):
    """
    http://www.ietf.org/rfc/rfc1035.txt
    The labels must follow the rules for ARPANET host names. They must
    start with a letter, end with a letter or digit, and have as interior
    characters only letters, digits, and hyphen.  There are also some
    restrictions on the length.  Labels must be 63 characters or less.
    """
    if not re.match(r'^[a-z][\.\-0-9a-z]*[\.0-9a-z]$', value):
        raise ValidationError(_("%s is not an appropiate zone label") % value)


def validate_record_name(value):
    if value not in ('', '@'):
        validate_zone_label(value)


def validate_mx_record(value):
    msg = _("%s is not an appropiate MX record value") % value
    value = value.split()
    if len(value) == 1:
        value = value[0]
    elif len(value) == 2:
        try:
            int(value[0])
        except ValueError:
            raise ValidationError(msg)
        value = value[1]
    elif len(value) > 2:
        raise ValidationError(msg)
    validate_zone_label(value)
