# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orchestration', '0002_auto_20150506_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='backendoperation',
            name='instance_repr',
            field=models.CharField(default='', max_length=256, verbose_name='instance representation'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='backendoperation',
            name='object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='route',
            name='async',
            field=models.BooleanField(default=False, help_text='Whether or not block the request/response cycle waitting this backend to finish its execution. Usually you want slave servers to run asynchronously.'),
        ),
    ]
