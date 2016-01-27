# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rate',
            name='plan',
            field=models.ForeignKey(related_name='rates', to='plans.Plan', blank=True, null=True, verbose_name='plan'),
        ),
    ]
