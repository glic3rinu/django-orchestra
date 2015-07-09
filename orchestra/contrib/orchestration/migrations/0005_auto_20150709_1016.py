# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('orchestration', '0004_route_async_actions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backendlog',
            name='created_at',
            field=models.DateTimeField(db_index=True, verbose_name='created', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='route',
            name='async_actions',
            field=orchestra.models.fields.MultiSelectField(blank=True, help_text='Specify individual actions to be executed asynchronoulsy.', max_length=256),
        ),
    ]
