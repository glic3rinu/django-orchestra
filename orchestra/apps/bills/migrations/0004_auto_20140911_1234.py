# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0003_bill_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='total',
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
    ]
