# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0010_auto_20140926_1326'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bill',
            name='last_modified_on',
        ),
        migrations.AddField(
            model_name='bill',
            name='updated_on',
            field=models.DateField(default=datetime.date(2014, 9, 26), verbose_name='updated on', auto_now=True),
            preserve_default=False,
        ),
    ]
