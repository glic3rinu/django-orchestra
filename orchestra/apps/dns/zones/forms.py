from django import forms

from . import settings


class RecordInlineFormSet(forms.models.BaseInlineFormSet):
    """ Provides initial record values """
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if not instance.pk and 'data' not in kwargs:
            records = settings.DNS_ZONE_DEFAULT_RECORDS
            total = len(records)
            prefix = kwargs['prefix']
            initial_data = {
                prefix+'-TOTAL_FORMS': unicode(total),
                prefix+'-INITIAL_FORMS': u'0',
                prefix+'-MAX_NUM_FORMS': unicode(total),
            }
            for num, record in enumerate(records):
                name, type, value = record
                initial_data[prefix+'-%d-name' % num] = name
                initial_data[prefix+'-%d-type' % num] = type
                initial_data[prefix+'-%d-value' % num] = value
            kwargs['data'] = initial_data
        super(RecordInlineFormSet, self).__init__(*args, **kwargs)

