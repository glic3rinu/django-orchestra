# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0002_auto_20150709_1018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='created_on',
        ),
        migrations.AddField(
            model_name='message',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 3, 20, 10, 27, 45, 766388, tzinfo=utc), verbose_name='created at'),
            preserve_default=False,
        ),
    ]
