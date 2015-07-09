# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='registered_on',
            field=models.DateField(db_index=True, default=django.utils.timezone.now, verbose_name='registered'),
        ),
    ]
