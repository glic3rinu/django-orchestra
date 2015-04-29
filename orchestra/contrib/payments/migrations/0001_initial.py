# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bills', '0002_auto_20150429_1417'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('method', models.CharField(choices=[('CreditCard', 'Credit card'), ('SEPADirectDebit', 'SEPA Direct Debit')], verbose_name='method', max_length=32)),
                ('data', jsonfield.fields.JSONField(verbose_name='data', default={})),
                ('is_active', models.BooleanField(verbose_name='active', default=True)),
                ('account', models.ForeignKey(verbose_name='account', related_name='paymentsources', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('state', models.CharField(choices=[('WAITTING_PROCESSING', 'Waitting processing'), ('WAITTING_EXECUTION', 'Waitting execution'), ('EXECUTED', 'Executed'), ('SECURED', 'Secured'), ('REJECTED', 'Rejected')], verbose_name='state', max_length=32, default='WAITTING_PROCESSING')),
                ('amount', models.DecimalField(verbose_name='amount', decimal_places=2, max_digits=12)),
                ('currency', models.CharField(max_length=10, default='Eur')),
                ('created_at', models.DateTimeField(verbose_name='created', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='modified', auto_now=True)),
                ('bill', models.ForeignKey(verbose_name='bill', related_name='transactions', to='bills.Bill')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionProcess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('data', jsonfield.fields.JSONField(blank=True, verbose_name='data')),
                ('file', models.FileField(blank=True, upload_to='', verbose_name='file')),
                ('state', models.CharField(choices=[('CREATED', 'Created'), ('EXECUTED', 'Executed'), ('ABORTED', 'Aborted'), ('COMMITED', 'Commited')], verbose_name='state', max_length=16, default='CREATED')),
                ('created_at', models.DateTimeField(verbose_name='created', auto_now_add=True)),
                ('updated_at', models.DateTimeField(verbose_name='updated', auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Transaction processes',
            },
        ),
        migrations.AddField(
            model_name='transaction',
            name='process',
            field=models.ForeignKey(verbose_name='process', null=True, blank=True, related_name='transactions', to='payments.TransactionProcess'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='source',
            field=models.ForeignKey(verbose_name='source', null=True, blank=True, related_name='transactions', to='payments.PaymentSource'),
        ),
    ]
