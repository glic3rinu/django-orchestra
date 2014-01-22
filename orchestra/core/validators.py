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
