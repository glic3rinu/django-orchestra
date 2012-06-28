from django.conf import settings

ugettext = lambda s: s

FIELD_TYPES = getattr(settings, 'FIELD_TYPES',(
    ('CharField', 'CharField'),
    ('BooleanField', 'BooleanField'),
    ('DateField', 'DateField'),
    ('DateTimeField', 'DateTimeField'),
    ('EmailField', 'EmailField'),
    ('FileField',  'FileField'),
    ('IntegerField',  'IntegerField'),
    ('IPAddressField', 'IPAddressField'),
))

DEFAUL_FIELD_TYPE = getattr(settings, 'DEFAUL_FIELD_TYPE', 'IntegerField')
