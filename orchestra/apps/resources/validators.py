from django.core.validators import ValidationError


def validate_scale(value):
    try:
        int(eval(value))
    except ValueError:
        raise ValidationError(_("%s value is not a valid scale expression"))
