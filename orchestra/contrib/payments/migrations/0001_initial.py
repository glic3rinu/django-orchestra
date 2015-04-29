# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bills', '0002_auto_20150429_1343'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('method', models.CharField(verbose_name='method', choices=[('SEPADirectDebit', 'SEPA Direct Debit')], max_length=32)),
                ('data', jsonfield.fields.JSONField(verbose_name='data', default={})),
                ('is_active', models.BooleanField(verbose_name='active', default=True)),
                ('account', models.ForeignKey(related_name='paymentsources', verbose_name='account', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('state', models.CharField(verbose_name='state', choices=[('WAITTING_PROCESSING', 'Waitting processing'), ('WAITTING_EXECUTION', 'Waitting execution'), ('EXECUTED', 'Executed'), ('SECURED', 'Secured'), ('REJECTED', 'Rejected')], max_length=32, default='WAITTING_PROCESSING')),
                ('amount', models.DecimalField(verbose_name='amount', max_digits=12, decimal_places=2)),
                ('currency', models.CharField(max_length=10, default='Eur')),
                ('created_at', models.DateTimeField(verbose_name='created', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='modified', auto_now=True)),
                ('bill', models.ForeignKey(related_name='transactions', verbose_name='bill', to='bills.Bill')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionProcess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('data', jsonfield.fields.JSONField(verbose_name='data', blank=True)),
                ('file', models.FileField(verbose_name='file', blank=True, upload_to='')),
                ('state', models.CharField(verbose_name='state', choices=[('CREATED', 'Created'), ('EXECUTED', 'Executed'), ('ABORTED', 'Aborted'), ('COMMITED', 'Commited')], max_length=16, default='CREATED')),
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
            field=models.ForeignKey(related_name='transactions', blank=True, null=True, verbose_name='process', to='payments.TransactionProcess'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='source',
            field=models.ForeignKey(related_name='transactions', blank=True, null=True, verbose_name='source', to='payments.PaymentSource'),
        ),
    ]
