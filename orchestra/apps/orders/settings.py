from django.conf import settings


ORDERS_CONTACT_MODEL = getattr(settings, 'ORDERS_CONTACT_MODEL', 'contacts.Contact')


ORDERS_COLLECTOR_MAX_DEPTH = getattr(settings, 'ORDERS_COLLECTOR_MAX_DEPTH', 3)
