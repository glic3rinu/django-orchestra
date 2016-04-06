# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vps', '0002_auto_20150804_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='vps',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='active'),
        ),
    ]
