import hashlib
import os
import re

from django.core.validators import ValidationError, EmailValidator
from django.utils.translation import ugettext_lazy as _

from orchestra.utils import paths
from orchestra.utils.sys import run

from . import settings


def validate_emailname(value):
    msg = _("'%s' is not a correct email name." % value)
    if '@' in value:
        raise ValidationError(msg)
    value += '@localhost'
    try:
        EmailValidator()(value)
    except ValidationError:
        raise ValidationError(msg)


def validate_forward(value):
    """ space separated mailboxes or emails """
    from .models import Mailbox
    errors = []
    destinations = []
    for destination in value.split():
        if destination in destinations:
            errors.append(ValidationError(
                _("'%s' is already present.") % destination
            ))
        destinations.append(destination)
        if '@' in destination:
            try:
                EmailValidator()(destination)
            except ValidationError:
                errors.append(ValidationError(
                    _("'%s' is not a valid email address.") % destination
                ))
        elif not Mailbox.objects.filter(name=destination).exists():
            errors.append(ValidationError(
                _("'%s' is not an existent mailbox.") % destination
            ))
    if errors:
        raise ValidationError(errors)


def validate_sieve(value):
    sieve_name = '%s.sieve' % hashlib.md5(value.encode('utf8')).hexdigest()
    test_path = os.path.join(settings.MAILBOXES_SIEVETEST_PATH, sieve_name)
    with open(test_path, 'w') as f:
        f.write(value)
    context = {
        'orchestra_root': paths.get_orchestra_dir()
    }
    sievetest = settings.MAILBOXES_SIEVETEST_BIN_PATH % context
    try:
        test = run(' '.join([sievetest, test_path, '/dev/null']), silent=True)
    finally:
        os.unlink(test_path)
    if test.exit_code:
        errors = []
        for line in test.stderr.decode('utf8').splitlines():
            error = re.match(r'^.*(line\s+[0-9]+:.*)', line)
            if error:
                errors += error.groups()
        raise ValidationError(' '.join(errors))
