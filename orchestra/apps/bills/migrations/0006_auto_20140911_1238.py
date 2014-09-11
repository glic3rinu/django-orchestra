# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0005_auto_20140911_1234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='budgetline',
            name='bill',
        ),
        migrations.DeleteModel(
            name='BudgetLine',
        ),
        migrations.DeleteModel(
            name='Budget',
        ),
        migrations.CreateModel(
            name='ProForma',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
        migrations.RemoveField(
            model_name='billline',
            name='auto',
        ),
        migrations.RemoveField(
            model_name='billline',
            name='order_billed_until',
        ),
        migrations.RemoveField(
            model_name='billline',
            name='order_id',
        ),
        migrations.RemoveField(
            model_name='billline',
            name='order_last_bill_date',
        ),
        migrations.AlterField(
            model_name='bill',
            name='type',
            field=models.CharField(max_length=16, verbose_name='type', choices=[(b'INVOICE', 'Invoice'), (b'AMENDMENTINVOICE', 'Amendment invoice'), (b'FEE', 'Fee'), (b'AMENDMENTFEE', 'Amendment Fee'), (b'PROFORMA', 'Pro forma')]),
        ),
        migrations.AlterField(
            model_name='billline',
            name='bill',
            field=models.ForeignKey(related_name=b'lines', verbose_name='bill', to='bills.Bill'),
        ),
    ]
