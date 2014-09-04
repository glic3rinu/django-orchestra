# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '__first__'),
        ('bills', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='payment_source',
            field=models.ForeignKey(blank=True, to='payments.PaymentSource', help_text='Optionally specify a payment source for this bill', null=True, verbose_name='payment source'),
            preserve_default=True,
        ),
    ]
