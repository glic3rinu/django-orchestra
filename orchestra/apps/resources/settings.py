from django.conf import settings

ugettext = lambda s: s


RESOURCES_RESOURCE_CHOICES = getattr(settings, 'RESOURCES_RESOURCE_CHOICES', ( ('Disk', ugettext('Disk')),
                                                           ('Traffic', ugettext('Traffic')),
                                                           ('CPU', ugettext('CPU')),
                                                           ('Memory', ugettext('Memory')),       
                                                           ('Swap', ugettext('Swap')),
                                                           ('Subscribers', ugettext('Subscribers')),
                                                           ))


RESOURCES_ALGORITHM_CHOICES = getattr(settings, 'RESOURCES_ALGORITHM_CHOICES', (('Last', ugettext('Last')),
                                                           ('Avg', ugettext('Average')),
                                                           ('Sum', ugettext('Sum')),
                                                           ('Max', ugettext('Max')),
                                                           ('Min', ugettext('Min')),
                                                           ))


RESOURCES_ALGORITHM_DEFAULT = getattr(settings, 'RESOURCES_ALGORITHM_DEFAULT', 'Last')


DAILY = 'D'
MONTHLY = 'M'
ANUAL = 'A'


RESOURCES_PERIOD_CHOICES = getattr(settings, 'RESOURCES_PERIOD_CHOICES', (('', ugettext('No Period')),
                                                     (DAILY, ugettext('Daily')),
                                                     (MONTHLY, ugettext('Monthly')),
                                                     (ANUAL, ugettext('Anual')),
                                                     ))


RESOURCES_TEMPLATE_PATHS = getattr(settings, 'RESOURCES_TEMPLATE_PATHS', ['/home/orchestra/orchestra/scripts/',])



