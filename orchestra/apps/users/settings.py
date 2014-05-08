from django.conf import settings


USERS_SYSTEMUSER_HOME = getattr(settings, 'USERES_SYSTEMUSER_HOME', '/home/%(username)s')
