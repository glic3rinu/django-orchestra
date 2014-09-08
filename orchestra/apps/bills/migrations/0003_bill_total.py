# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0002_bill_closed_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='total',
            field=models.DecimalField(default=10, max_digits=12, decimal_places=2),
            preserve_default=False,
        ),
    ]
