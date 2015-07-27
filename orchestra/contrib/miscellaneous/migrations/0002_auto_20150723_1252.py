# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('miscellaneous', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='miscellaneous',
            name='identifier',
            field=orchestra.models.fields.NullableCharField(db_index=True, unique=True, help_text='A unique identifier for this service.', null=True, max_length=256, verbose_name='identifier'),
        ),
    ]
