# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcedata',
            name='used',
            field=models.DecimalField(verbose_name='used', null=True, editable=False, max_digits=16, decimal_places=3),
            preserve_default=True,
        ),
    ]
