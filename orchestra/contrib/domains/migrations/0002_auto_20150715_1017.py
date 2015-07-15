# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='expire',
            field=models.IntegerField(null=True, blank=True, help_text='The upper limit in seconds before a zone is considered no longer authoritative (4w by default).', verbose_name='expire'),
        ),
        migrations.AddField(
            model_name='domain',
            name='min_ttl',
            field=models.IntegerField(null=True, blank=True, help_text='The negative result TTL (for example, how long a resolver should consider a negative result for a subdomain to be valid before retrying) (1h by default).', verbose_name='refresh'),
        ),
        migrations.AddField(
            model_name='domain',
            name='refresh',
            field=models.IntegerField(null=True, blank=True, help_text='The number of seconds before the zone should be refreshed (1d by default).', verbose_name='refresh'),
        ),
        migrations.AddField(
            model_name='domain',
            name='retry',
            field=models.IntegerField(null=True, blank=True, help_text='The number of seconds before a failed refresh should be retried (2h by default).', verbose_name='retry'),
        ),
        migrations.AlterField(
            model_name='record',
            name='value',
            field=models.CharField(max_length=256, help_text='MX, NS and CNAME records sould end with a dot.', verbose_name='value'),
        ),
    ]
