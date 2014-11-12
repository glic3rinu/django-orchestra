from django.conf import settings


MISCELLANEOUS_IDENTIFIER_VALIDATORS = getattr(settings, MISCELLANEOUS_IDENTIFIER_VALIDATORS, {})
# MISCELLANEOUS_IDENTIFIER_VALIDATORS = { miscservice__name: validator_function }
