# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.contrib.domains.validators


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0003_auto_20150720_1121'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='expire',
            field=models.CharField(validators=[orchestra.contrib.domains.validators.validate_zone_interval], blank=True, help_text='The time that a secondary server will keep trying to complete a zone transfer. If this time expires prior to a successful zone transfer, the secondary server will expire its zone file. This means the secondary will stop answering queries. The default value is <tt>4w</tt>.', verbose_name='expire', max_length=16),
        ),
        migrations.AddField(
            model_name='domain',
            name='min_ttl',
            field=models.CharField(validators=[orchestra.contrib.domains.validators.validate_zone_interval], blank=True, help_text='The minimum time-to-live value applies to all resource records in the zone file. This value is supplied in query responses to inform other servers how long they should keep the data in cache. The default value is <tt>1h</tt>.', verbose_name='min TTL', max_length=16),
        ),
        migrations.AddField(
            model_name='domain',
            name='refresh',
            field=models.CharField(validators=[orchestra.contrib.domains.validators.validate_zone_interval], blank=True, help_text="The time a secondary DNS server waits before querying the primary DNS server's SOA record to check for changes. When the refresh time expires, the secondary DNS server requests a copy of the current SOA record from the primary. The primary DNS server complies with this request. The secondary DNS server compares the serial number of the primary DNS server's current SOA record and the serial number in it's own SOA record. If they are different, the secondary DNS server will request a zone transfer from the primary DNS server. The default value is <tt>1d</tt>.", verbose_name='refresh', max_length=16),
        ),
        migrations.AddField(
            model_name='domain',
            name='retry',
            field=models.CharField(validators=[orchestra.contrib.domains.validators.validate_zone_interval], blank=True, help_text='The time a secondary server waits before retrying a failed zone transfer. Normally, the retry time is less than the refresh time. The default value is <tt>2h</tt>.', verbose_name='retry', max_length=16),
        ),
    ]
