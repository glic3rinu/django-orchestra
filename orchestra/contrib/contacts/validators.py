from orchestra.core import validators

from . import settings


def validate_phone(phone):
    validators.validate_phone(phone, settings.CONTACTS_DEFAULT_COUNTRY)
