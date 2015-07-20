# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.contrib.domains.utils


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0002_auto_20150715_1017'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='domain',
            name='expire',
        ),
        migrations.RemoveField(
            model_name='domain',
            name='min_ttl',
        ),
        migrations.RemoveField(
            model_name='domain',
            name='refresh',
        ),
        migrations.RemoveField(
            model_name='domain',
            name='retry',
        ),
        migrations.AlterField(
            model_name='domain',
            name='serial',
            field=models.IntegerField(editable=False, verbose_name='serial', default=orchestra.contrib.domains.utils.generate_zone_serial, help_text='A revision number that changes whenever this domain is updated.'),
        ),
    ]
