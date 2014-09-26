# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20140909_1850'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='register_date',
        ),
        migrations.AddField(
            model_name='account',
            name='registered_on',
            field=models.DateField(default=datetime.datetime(2014, 9, 26, 13, 25, 49, 42008), verbose_name='registered', auto_now_add=True),
            preserve_default=False,
        ),
    ]
