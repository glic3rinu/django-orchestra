# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0006_auto_20140911_1238'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bill',
            name='status',
        ),
        migrations.RemoveField(
            model_name='billline',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='billline',
            name='total',
        ),
        migrations.AddField(
            model_name='bill',
            name='is_open',
            field=models.BooleanField(default=True, verbose_name='is open'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bill',
            name='is_sent',
            field=models.BooleanField(default=False, verbose_name='is sent'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='billline',
            name='quantity',
            field=models.DecimalField(default=10, verbose_name='quantity', max_digits=12, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='billline',
            name='subtotal',
            field=models.DecimalField(default=20, verbose_name='subtotal', max_digits=12, decimal_places=2),
            preserve_default=False,
        ),
    ]
