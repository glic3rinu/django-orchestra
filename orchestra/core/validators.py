import re

import crack
import localflavor
import phonenumbers

from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from IPy import IP

from ..utils.python import import_class


def all_valid(kwargs):
    """ helper function to merge multiple validators at once """
    errors = {}
    for field, validator in kwargs.iteritems():
        try:
            validator[0](*validator[1:])
        except ValidationError, error:
            errors[field] = error
    if errors:
        raise ValidationError(errors)


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
    validators.RegexValidator('^[\.\_\-0-9a-z]+$',
        _("Enter a valid name (spaceless lowercase text including _.-)."), 'invalid')(value)


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
        raise ValidationError(_("Too long for a hostname."))
    hostname = hostname.rstrip('.')
    allowed = re.compile('(?!-)[A-Z\d-]{1,63}(?<!-)$', re.IGNORECASE)
    for name in hostname.split('.'):
        if not allowed.match(name):
            raise ValidationError(_("Not a valid hostname (%s).") % name)


def validate_password(value):
    try:
        crack.VeryFascistCheck(value)
    except ValueError, message:
        raise ValidationError("Password %s." % str(message)[3:])


def validate_url_path(value):
    if not re.match(r'^\/[/.a-zA-Z0-9-_]*$', value):
        raise ValidationError(_('"%s" is not a valid URL path.') % value)


def validate_vat(vat, country):
    field = 'localflavor.{lower}.forms.{upper}IdentityCardNumberField'.format(
        lower=country.lower(),
        upper=country.upper()
    )
    try:
        field = import_class(field)
    except (ImportError, AttributeError, ValueError):
        pass
    else:
        field().clean(vat)


def validate_zipcode(zipcode, country):
    field = 'localflavor.{lower}.forms.{upper}PostalCodeField'.format(
        lower=country.lower(),
        upper=country.upper()
    )
    try:
        field = import_class(field)
    except (ImportError, AttributeError, ValueError):
        pass
    else:
        field().clean(zipcode)


def validate_phone(value, country):
    """ local phone number or international """
    msg = _("Not a valid %s nor international phone number.") % country
    try:
        number = phonenumbers.parse(value, country)
    except phonenumbers.phonenumberutil.NumberParseException:
        raise ValidationError(msg)
    if not phonenumbers.is_valid_number(number):
        raise ValidationError(msg)
