from django.conf import settings

ugettext = lambda s: s

EXTRA_FIELDS_FIELD_TYPES = getattr(settings, 'EXTRA_FIELDS_FIELD_TYPES',(
    ('CharField', 'CharField'),
    ('BooleanField', 'BooleanField'),
    ('DateField', 'DateField'),
    ('DateTimeField', 'DateTimeField'),
    ('EmailField', 'EmailField'),
    ('FileField',  'FileField'),
    ('IntegerField',  'IntegerField'),
    ('IPAddressField', 'IPAddressField'),
))

EXTRA_FIELDS_DEFAUL_FIELD_TYPE = getattr(settings, 'EXTRA_FIELDS_DEFAUL_FIELD_TYPE', 'IntegerField')
