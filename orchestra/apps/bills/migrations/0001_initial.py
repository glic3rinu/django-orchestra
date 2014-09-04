# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(unique=True, max_length=16, verbose_name='number', blank=True)),
                ('type', models.CharField(max_length=16, verbose_name='type', choices=[(b'INVOICE', 'Invoice'), (b'AMENDMENTINVOICE', 'Amendment invoice'), (b'FEE', 'Fee'), (b'AMENDMENTFEE', 'Amendment Fee'), (b'BUDGET', 'Budget')])),
                ('status', models.CharField(default=b'OPEN', max_length=16, verbose_name='status', choices=[(b'OPEN', 'Open'), (b'CLOSED', 'Closed'), (b'SENT', 'Sent'), (b'PAID', 'Paid'), (b'RETURNED', 'Returned'), (b'BAD_DEBT', 'Bad debt')])),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('due_on', models.DateField(null=True, verbose_name='due on', blank=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, verbose_name='last modified on')),
                ('comments', models.TextField(verbose_name='comments', blank=True)),
                ('html', models.TextField(verbose_name='HTML', blank=True)),
                ('account', models.ForeignKey(related_name=b'bill', verbose_name='account', to='accounts.Account')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BillLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=256, verbose_name='description')),
                ('rate', models.DecimalField(null=True, verbose_name='rate', max_digits=12, decimal_places=2, blank=True)),
                ('amount', models.DecimalField(verbose_name='amount', max_digits=12, decimal_places=2)),
                ('total', models.DecimalField(verbose_name='total', max_digits=12, decimal_places=2)),
                ('tax', models.PositiveIntegerField(verbose_name='tax')),
                ('order_id', models.PositiveIntegerField(null=True, blank=True)),
                ('order_last_bill_date', models.DateTimeField(null=True)),
                ('order_billed_until', models.DateTimeField(null=True)),
                ('auto', models.BooleanField(default=False)),
                ('amended_line', models.ForeignKey(related_name=b'amendment_lines', verbose_name='amended line', blank=True, to='bills.BillLine', null=True)),
                ('bill', models.ForeignKey(related_name=b'billlines', verbose_name='bill', to='bills.Bill')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BillSubline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=256, verbose_name='description')),
                ('total', models.DecimalField(max_digits=12, decimal_places=2)),
                ('bill_line', models.ForeignKey(related_name=b'sublines', verbose_name='bill line', to='bills.BillLine')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BudgetLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=256, verbose_name='description')),
                ('rate', models.DecimalField(null=True, verbose_name='rate', max_digits=12, decimal_places=2, blank=True)),
                ('amount', models.DecimalField(verbose_name='amount', max_digits=12, decimal_places=2)),
                ('total', models.DecimalField(verbose_name='total', max_digits=12, decimal_places=2)),
                ('tax', models.PositiveIntegerField(verbose_name='tax')),
                ('bill', models.ForeignKey(related_name=b'budgetlines', verbose_name='bill', to='bills.Bill')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AmendmentFee',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
        migrations.CreateModel(
            name='AmendmentInvoice',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
        migrations.CreateModel(
            name='Budget',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
        migrations.CreateModel(
            name='Fee',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
    ]
