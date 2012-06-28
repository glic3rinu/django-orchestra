from django.conf import settings

ugettext = lambda s: s


DAEMONS_TEMPLATE_PATHS = getattr(settings, 'DAEMONS_TEMPLATE_PATHS', ['/home/ucp/trunk/ucp/daemons/templates/scripts/',])


LINUX = 'L'
WINDOWS = 'W'
BSD = 'B'


DAEMONS_OS_CHOICES = getattr(settings, 'DAEMONS_OS_CHOICES', ((LINUX, 'Linux'),
                                              (WINDOWS, 'Windows'),
                                              (BSD, 'BSD'),))


DAEMONS_DEFAULT_OS_CHOICE = getattr(settings, 'DAEMONS_DEFAULT_OS_CHOICE', LINUX)


PYTHON = 'P'
SSH = 'S'
LOCAL ='L'


DAEMONS_METHOD_CHOICES = getattr(settings, 'DAEMONS_METHOD_CHOICES', ((PYTHON, 'Exec Python code'),
                                                                      (SSH, 'Run script through SSH'),
                                                                      (LOCAL, 'Run Local script'),))
DAEMONS_DEFAULT_METHOD_CHOICE = getattr(settings, 'DAEMONS_DEFAULT_METHOD_CHOICE', SSH)

#TODO: deprecate this shit?
DAEMONS_SAVE_SIGNALS = getattr(settings, 'DAEMONS_SAVE_SIGNALS', (('django.db.models.signals.post_save', 'model post_save'),
                                                  ('django.db.models.signals.pre_save', 'model pre_save'),
                                                  ('signals.service_created', 'service created'),
                                                  ))
DAEMONS_DEFAULT_SAVE_SIGNAL = getattr(settings, 'DAEMONS_DEFAULT_SAVE_SIGNAL', 'signals.service_created')

DAEMONS_DELETE_SIGNALS = getattr(settings, 'DAEMONS_DELETE_SIGNALS', (('django.db.models.signals.post_delete', 'model post_delete'),
                                                  ('django.db.models.signals.pre_delete', 'model pre_delete'),
                                                  ('signals.service_deleted', 'service delete'),
                                                  ))

DAEMONS_DEFAULT_DELETE_SIGNAL = getattr(settings, 'DAEMONS_DEFAULT_DELETE_SIGNAL', 'signals.service_deleted')


DAEMONS_LOCK_EXPIRE = getattr(settings, 'DAEMONS_LOCL_EXPORE', 60 * 2 )
