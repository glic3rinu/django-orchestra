import re

import crack

from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from IPy import IP


def validate_ipv4_address(value):
    msg = _("%s is not a valid IPv4 address") % value
    try:
        ip = IP(value)
    except:
        raise ValidationError(msg)
    if ip.version() != 4:
        raise ValidationError(msg)



def validate_ipv6_address(value):
    msg = _("%s is not a valid IPv6 address") % value
    try:
        ip = IP(value)
    except:
        raise ValidationError(msg)
    if ip.version() != 6:
        raise ValidationError(msg)


def validate_ip_address(value):
    msg = _("%s is not a valid IP address") % value
    try:
        ip = IP(value)
    except:
        raise ValidationError(msg)


def validate_name(value):
    """
    A single non-empty line of free-form text with no whitespace.
    """
    validators.RegexValidator('^[\.\w]+$',
        _("Enter a valid name (text without whitspaces)."), 'invalid')(value)


def validate_ascii(value):
    try:
        value.decode('ascii')
    except UnicodeDecodeError:
        raise ValidationError('This is not an ASCII string.')


def validate_hostname(hostname):
    """
    Ensures that each segment
      * contains at least one character and a maximum of 63 characters
      * consists only of allowed characters
      * doesn't begin or end with a hyphen.
    http://stackoverflow.com/a/2532344
    """
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def validate_password(value):
    try:
        crack.VeryFascistCheck(value)
    except ValueError, message:
        raise ValidationError("Password %s." % str(message)[3:])

