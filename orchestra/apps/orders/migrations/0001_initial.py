# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '__first__'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetricStorage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.BigIntegerField(verbose_name='value')),
                ('created_on', models.DateField(auto_now_add=True, verbose_name='created on')),
                ('updated_on', models.DateField(auto_now=True, verbose_name='updated on')),
            ],
            options={
                'get_latest_by': 'created_on',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('registered_on', models.DateField(auto_now_add=True, verbose_name='registered on')),
                ('cancelled_on', models.DateField(null=True, verbose_name='cancelled on', blank=True)),
                ('billed_on', models.DateField(null=True, verbose_name='billed on', blank=True)),
                ('billed_until', models.DateField(null=True, verbose_name='billed until', blank=True)),
                ('ignore', models.BooleanField(default=False, verbose_name='ignore')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('account', models.ForeignKey(related_name=b'orders', verbose_name='account', to='accounts.Account')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(unique=True, max_length=256, verbose_name='description')),
                ('match', models.CharField(max_length=256, verbose_name='match', blank=True)),
                ('handler_type', models.CharField(blank=True, help_text='Handler used for processing this Service. A handler enables customized behaviour far beyond what options here allow to.', max_length=256, verbose_name='handler', choices=[(b'', 'Default')])),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('billing_period', models.CharField(default=b'ANUAL', choices=[(b'', 'One time service'), (b'MONTHLY', 'Monthly billing'), (b'ANUAL', 'Anual billing')], max_length=16, blank=True, help_text='Renewal period for recurring invoicing', verbose_name='billing period')),
                ('billing_point', models.CharField(default=b'ON_FIXED_DATE', help_text='Reference point for calculating the renewal date on recurring invoices', max_length=16, verbose_name='billing point', choices=[(b'ON_REGISTER', 'Registration date'), (b'ON_FIXED_DATE', 'Fixed billing date')])),
                ('delayed_billing', models.CharField(default=b'ONE_MONTH', choices=[(b'', 'No delay (inmediate billing)'), (b'TEN_DAYS', 'Ten days'), (b'ONE_MONTH', 'One month')], max_length=16, blank=True, help_text='Period in which this service will be ignored for billing', verbose_name='delayed billing')),
                ('is_fee', models.BooleanField(default=False, help_text='Designates whether this service should be billed as  membership fee or not', verbose_name='is fee')),
                ('metric', models.CharField(help_text='Metric used to compute the pricing rate. Number of orders is used when left blank.', max_length=256, verbose_name='metric', blank=True)),
                ('tax', models.PositiveIntegerField(default=0, verbose_name='tax', choices=[(0, 'Duty free'), (7, '7%'), (21, '21%')])),
                ('pricing_period', models.CharField(default=b'BILLING_PERIOD', help_text='Period used for calculating the metric used on the pricing rate', max_length=16, verbose_name='pricing period', choices=[(b'BILLING_PERIOD', 'Same as billing period'), (b'MONTHLY', 'Monthly data'), (b'ANUAL', 'Anual data')])),
                ('rate_algorithm', models.CharField(default=b'BEST_PRICE', help_text='Algorithm used to interprete the rating table', max_length=16, verbose_name='rate algorithm', choices=[(b'BEST_PRICE', 'Best progressive price'), (b'PROGRESSIVE_PRICE', 'Conservative progressive price'), (b'MATCH_PRICE', 'Match price')])),
                ('orders_effect', models.CharField(default=b'CONCURRENT', help_text='Defines the lookup behaviour when using orders for the pricing rate computation of this service.', max_length=16, verbose_name='orders effect', choices=[(b'REGISTER_OR_RENEW', 'Register or renew events'), (b'CONCURRENT', 'Active at every given time')])),
                ('on_cancel', models.CharField(default=b'DISCOUNT', help_text='Defines the cancellation behaviour of this service', max_length=16, verbose_name='on cancel', choices=[(b'NOTHING', 'Nothing'), (b'DISCOUNT', 'Discount'), (b'COMPENSATE', 'Discount and compensate'), (b'REFOUND', 'Discount, compensate and refound')])),
                ('payment_style', models.CharField(default=b'PREPAY', help_text='Designates whether this service should be paid after consumtion (postpay/on demand) or prepaid', max_length=16, verbose_name='payment style', choices=[(b'PREPAY', 'Prepay'), (b'POSTPAY', 'Postpay (on demand)')])),
                ('trial_period', models.CharField(default=b'', choices=[(b'', 'No trial'), (b'TEN_DAYS', 'Ten days'), (b'ONE_MONTH', 'One month')], max_length=16, blank=True, help_text='Period in which no charge will be issued', verbose_name='trial period')),
                ('refound_period', models.CharField(default=b'', choices=[(b'', 'Never refound'), (b'TEN_DAYS', 'Ten days'), (b'ONE_MONTH', 'One month'), (b'ALWAYS', 'Always refound')], max_length=16, blank=True, help_text='Period in which automatic refound will be performed on service cancellation', verbose_name='refound period')),
                ('content_type', models.ForeignKey(verbose_name='content type', to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='order',
            name='service',
            field=models.ForeignKey(related_name=b'orders', verbose_name='service', to='orders.Service'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='metricstorage',
            name='order',
            field=models.ForeignKey(verbose_name='order', to='orders.Order'),
            preserve_default=True,
        ),
    ]
