# -*- coding: utf-8 -*-

from django.db import models, migrations
import orchestra.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('miscellaneous', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='miscellaneous',
            name='identifier',
            field=orchestra.models.fields.NullableCharField(help_text='A unique identifier for this service.', max_length=256, unique=True, null=True, verbose_name='identifier'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='miscservice',
            name='has_identifier',
            field=models.BooleanField(default=True, help_text='Designates if this service has a <b>unique text</b> field that identifies it or not.', verbose_name='has identifier'),
            preserve_default=True,
        ),
    ]
