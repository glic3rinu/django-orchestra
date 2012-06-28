from django.conf import settings

ugettext = lambda s: s


RESOURCE_CHOICES = getattr(settings, 'RESOURCE_CHOICES', ( ('Disk', ugettext('Disk')),
                                                           ('Traffic', ugettext('Traffic')),
                                                           ('CPU', ugettext('CPU')),
                                                           ('Memory', ugettext('Memory')),       
                                                           ('Swap', ugettext('Swap')),
                                                           ('Subscribers', ugettext('Subscribers')),
                                                           ))


ALGORITHM_CHOICES = getattr(settings, 'ALGORITHM_CHOICES', (('Last', ugettext('Last')),
                                                           ('Avg', ugettext('Average')),
                                                           ('Sum', ugettext('Sum')),
                                                           ('Max', ugettext('Max')),
                                                           ('Min', ugettext('Min')),
                                                           ))


ALGORITHM_DEFAULT = getattr(settings, 'ALGORITHM_DEFAULT', 'Last')


DAILY = 'D'
MONTHLY = 'M'
ANUAL = 'A'


PERIOD_CHOICES = getattr(settings, 'PERIOD_CHOICES', (('', ugettext('No Period')),
                                                     (DAILY, ugettext('Daily')),
                                                     (MONTHLY, ugettext('Monthly')),
                                                     (ANUAL, ugettext('Anual')),
                                                     ))


TEMPLATE_PATHS = getattr(settings, 'TEMPLATE_PATHS', ['/home/orchestra/panel/templates/scripts/',])



