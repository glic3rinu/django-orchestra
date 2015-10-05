from django.core.validators import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_scale(value):
    try:
        int(eval(value))
    except Exception as e:
        raise ValidationError(
            _("'%s' is not a valid scale expression. (%s)") % (value, e)
        )
