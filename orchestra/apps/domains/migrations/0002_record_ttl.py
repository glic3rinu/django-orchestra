# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.apps.domains.validators


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='ttl',
            field=models.CharField(default='', validators=[orchestra.apps.domains.validators.validate_zone_interval], max_length=8, blank=True, help_text='Record TTL, defaults to 1h', verbose_name='TTL'),
            preserve_default=False,
        ),
    ]
