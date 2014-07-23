from django.conf import settings


PAYMENT_CURRENCY = getattr(settings, 'PAYMENT_CURRENCY', 'Eur')
