from django.conf import settings

ugettext = lambda s: s

DEFAULT_SSH_USER = getattr(settings, 'DEFAULT_SSH_USER', 'root')                 
                                         
DEFAULT_SSH_PORT = getattr(settings, 'DEFAULT_SSH_PORT', 22)                                                       

DEFAULT_SSH_HOST_KEYS = getattr(settings, 'DEFAULT_SSH_HOST_KEYS', '/home/glic3rinu/.ssh/known_hosts')                                                              
