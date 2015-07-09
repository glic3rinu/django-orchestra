# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import orchestra.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentsource',
            name='method',
            field=models.CharField(max_length=32, verbose_name='method', choices=[('SEPADirectDebit', 'SEPA Direct Debit')]),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='process',
            field=models.ForeignKey(verbose_name='process', on_delete=django.db.models.deletion.SET_NULL, blank=True, related_name='transactions', to='payments.TransactionProcess', null=True),
        ),
        migrations.AlterField(
            model_name='transactionprocess',
            name='created_at',
            field=models.DateTimeField(db_index=True, verbose_name='created', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='transactionprocess',
            name='file',
            field=orchestra.models.fields.PrivateFileField(blank=True, verbose_name='file', upload_to=''),
        ),
    ]
