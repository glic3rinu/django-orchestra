# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0003_auto_20150502_1433'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CrontabSchedule',
        ),
    ]
