# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='rate_algorithm',
            field=models.CharField(choices=[('orchestra.contrib.plans.rating.best_price', 'Best price'), ('orchestra.contrib.plans.rating.step_price', 'Step price'), ('orchestra.contrib.plans.rating.match_price', 'Match price')], help_text='Algorithm used to interprete the rating table.<br>&nbsp;&nbsp;Best price: Produces the best possible price given all active rating lines.<br>&nbsp;&nbsp;Step price: All rates with a quantity lower than the metric are applied. Nominal price will be used when initial block is missing.<br>&nbsp;&nbsp;Match price: Only <b>the rate</b> with a) inmediate inferior metric and b) lower price is applied. Nominal price will be used when initial block is missing.', max_length=64, verbose_name='rate algorithm', default='orchestra.contrib.plans.rating.step_price'),
        ),
        migrations.AlterField(
            model_name='service',
            name='tax',
            field=models.PositiveIntegerField(choices=[(0, 'Duty free'), (21, '21%')], verbose_name='tax', default=21),
        ),
    ]
