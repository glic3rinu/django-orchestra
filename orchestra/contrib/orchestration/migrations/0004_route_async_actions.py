# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('orchestration', '0003_auto_20150512_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='async_actions',
            field=orchestra.models.fields.MultiSelectField(blank=True, max_length=256),
        ),
    ]
