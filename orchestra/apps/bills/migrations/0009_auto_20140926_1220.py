# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '__first__'),
        ('bills', '0008_auto_20140926_1218'),
    ]

    operations = [
        migrations.AddField(
            model_name='billline',
            name='created_on',
            field=models.DateField(default=datetime.datetime(2014, 9, 26, 12, 20, 24, 908200), verbose_name='created', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='billline',
            name='order_billed_on',
            field=models.DateField(null=True, verbose_name='order billed', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='billline',
            name='order_billed_until',
            field=models.DateField(null=True, verbose_name='order billed until', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='billline',
            name='order_id',
            field=models.ForeignKey(blank=True, to='orders.Order', help_text='Informative link back to the order', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='billsubline',
            name='type',
            field=models.CharField(default=b'OTHER', max_length=16, verbose_name='type', choices=[(b'VOLUME', 'Volume'), (b'COMPENSATION', 'Compensation'), (b'OTHER', 'Other')]),
            preserve_default=True,
        ),
    ]
