# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='nominal_price',
            field=models.DecimalField(default=0.0, verbose_name='nominal price', max_digits=12, decimal_places=2),
            preserve_default=False,
        ),
    ]
