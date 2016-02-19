import logging
import re
from ipaddress import ip_address

import phonenumbers
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _

from ..utils.python import import_class


logger = logging.getLogger(__name__)


def all_valid(*args):
    """ helper function to merge multiple validators at once """
    if len(args) == 1:
        # Dict
        errors = {}
        kwargs = args[0]
        for field, validator in kwargs.items():
            try:
                validator[0](*validator[1:])
            except ValidationError as error:
                errors[field] = error
    else:
        # List
        errors = []
        value, validators = args
        for validator in validators:
            try:
                validator(value)
            except ValidationError as error:
                errors.append(error)
    if errors:
        raise ValidationError(errors)


@deconstructible
class OrValidator(object):
    """
    Run validators with an OR logic
    """
    def __init__(self, *validators):
        self.validators = validators
    
    def __call__(self, value):
        msg = []
        for validator in self.validators:
            try:
                validator(value)
            except ValidationError as err:
                msg.append(str(err))
            else:
                return
        raise ValidationError(' OR '.join(msg))


def validate_ipv4_address(value):
    msg = _("Not a valid IPv4 address")
    try:
        ip = ip_address(value)
    except ValueError:
        raise ValidationError(msg)
    if ip.version != 4:
        raise ValidationError(msg)


def validate_ipv6_address(value):
    msg = _("Not a valid IPv6 address")
    try:
        ip = ip_address(value)
    except ValueError:
        raise ValidationError(msg)
    if ip.version != 6:
        raise ValidationError(msg)


def validate_ip_address(value):
    msg = _("Not a valid IP address")
    try:
        ip_address(value)
    except ValueError:
        raise ValidationError(msg)


def validate_name(value):
    """
    A single non-empty line of free-form text with no whitespace.
    """
    validators.RegexValidator('^[\.\_\-0-9a-z]+$',
        _("Enter a valid name (spaceless lowercase text including _.-)."), 'invalid')(value)


def validate_ascii(value):
    try:
        value.encode('ascii')
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


def validate_username(value):
    validators.RegexValidator(r'^[\w.-]+$', _("Enter a valid username."))(value)


def validate_password(value):
    try:
        import crack
    except:
        try:
            import cracklib as crack
        except:
            logger.error("Can not validate password. Cracklib bindings are not installed.")
            return
    try:
        crack.VeryFascistCheck(value)
    except ValueError as message:
        raise ValidationError("Password %s." % str(message)[3:])


def validate_url_path(value):
    if not re.match(r'^\/[/.a-zA-Z0-9-_]*$', value):
        raise ValidationError(_('"%s" is not a valid URL-path.') % value)


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
