from django.conf import settings


USERS_SYSTEMUSER_HOME = getattr(settings, 'USERES_SYSTEMUSER_HOME', '/home/%(username)s')

USERS_FTP_LOG_PATH = getattr(settings, 'USERS_FTP_LOG_PATH', '/var/log/vsftpd.log')
