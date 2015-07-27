# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0006_auto_20150723_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcedata',
            name='object_id',
            field=models.PositiveIntegerField(verbose_name='object id', db_index=True),
        ),
    ]
