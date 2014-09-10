# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20140908_1409'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rate',
            name='value',
        ),
        migrations.AddField(
            model_name='rate',
            name='price',
            field=models.DecimalField(default=1, verbose_name='price', max_digits=12, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='rate',
            name='plan',
            field=models.CharField(blank=True, max_length=128, verbose_name='plan', choices=[(b'', 'Default'), (b'basic', 'Basic'), (b'advanced', 'Advanced')]),
        ),
    ]
