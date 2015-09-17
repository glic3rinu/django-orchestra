# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_auto_20150509_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='billing_point',
            field=models.CharField(choices=[('ON_REGISTER', 'Registration date'), ('ON_FIXED_DATE', 'Every April')], help_text='Reference point for calculating the renewal date on recurring invoices', verbose_name='billing point', max_length=16, default='ON_FIXED_DATE'),
        ),
        migrations.AlterField(
            model_name='service',
            name='is_fee',
            field=models.BooleanField(help_text='Designates whether this service should be billed as membership fee or not', verbose_name='fee', default=False),
        ),
        migrations.AlterField(
            model_name='service',
            name='order_description',
            field=models.CharField(help_text="Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> used for generating the description for the bill lines of this services.<br>Defaults to <tt>'%s: %s' % (ugettext(handler.description), instance)</tt>", blank=True, max_length=256, verbose_name='Order description'),
        ),
        migrations.AlterField(
            model_name='service',
            name='rate_algorithm',
            field=models.CharField(choices=[('orchestra.contrib.plans.ratings.step_price', 'Step price'), ('orchestra.contrib.plans.ratings.best_price', 'Best price'), ('orchestra.contrib.plans.ratings.match_price', 'Match price')], help_text='Algorithm used to interprete the rating table.<br>&nbsp;&nbsp;Step price: All rates with a quantity lower or equal than the metric are applied. Nominal price will be used when initial block is missing.<br>&nbsp;&nbsp;Best price: Produces the best possible price given all active rating lines (those with quantity lower or equal to the metric).<br>&nbsp;&nbsp;Match price: Only <b>the rate</b> with a) inmediate inferior metric and b) lower price is applied. Nominal price will be used when initial block is missing.', verbose_name='rate algorithm', max_length=64, default='orchestra.contrib.plans.ratings.step_price'),
        ),
    ]
