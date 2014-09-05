# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='closed_on',
            field=models.DateTimeField(null=True, verbose_name='closed on', blank=True),
            preserve_default=True,
        ),
    ]
