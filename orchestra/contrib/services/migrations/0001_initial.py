# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('description', models.CharField(verbose_name='description', max_length=256, unique=True)),
                ('match', models.CharField(verbose_name='match', help_text="Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> that designates wheter a <tt>content_type</tt> object is related to this service or not, always evaluates <tt>True</tt> when left blank. Related instance can be instantiated with <tt>instance</tt> keyword or <tt>content_type.model_name</tt>.</br><tt>&nbsp;databaseuser.type == 'MYSQL'</tt><br><tt>&nbsp;miscellaneous.active and str(miscellaneous.identifier).endswith(('.org', '.net', '.com'))</tt><br><tt>&nbsp;contractedplan.plan.name == 'association_fee''</tt><br><tt>&nbsp;instance.active</tt>", max_length=256, blank=True)),
                ('handler_type', models.CharField(verbose_name='handler', help_text='Handler used for processing this Service. A handler enables customized behaviour far beyond what options here allow to.', max_length=256, blank=True, choices=[('', 'Default')])),
                ('is_active', models.BooleanField(verbose_name='active', default=True)),
                ('ignore_superusers', models.BooleanField(verbose_name='ignore superuser, staff and friend', help_text='Designates whether superuser, staff and friend orders are marked as ignored by default or not.', default=True)),
                ('billing_period', models.CharField(verbose_name='billing period', help_text='Renewal period for recurring invoicing.', blank=True, choices=[('', 'One time service'), ('MONTHLY', 'Monthly billing'), ('ANUAL', 'Anual billing')], max_length=16, default='ANUAL')),
                ('billing_point', models.CharField(verbose_name='billing point', help_text='Reference point for calculating the renewal date on recurring invoices', max_length=16, default='ON_FIXED_DATE', choices=[('ON_REGISTER', 'Registration date'), ('ON_FIXED_DATE', 'Fixed billing date')])),
                ('is_fee', models.BooleanField(verbose_name='fee', help_text='Designates whether this service should be billed as  membership fee or not', default=False)),
                ('order_description', models.CharField(verbose_name='Order description', help_text="Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> used for generating the description for the bill lines of this services.<br>Defaults to <tt>'%s: %s' % (handler.description, instance)</tt>", max_length=128, blank=True)),
                ('ignore_period', models.CharField(verbose_name='ignore period', help_text='Period in which orders will be ignored if cancelled. Useful for designating <i>trial periods</i>', blank=True, choices=[('', 'Never'), ('ONE_DAY', 'One day'), ('TWO_DAYS', 'Two days'), ('TEN_DAYS', 'Ten days'), ('ONE_MONTH', 'One month')], max_length=16, default='TEN_DAYS')),
                ('metric', models.CharField(verbose_name='metric', help_text="Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> used for obtinging the <i>metric value</i> for the pricing rate computation. Number of orders is used when left blank. Related instance can be instantiated with <tt>instance</tt> keyword or <tt>content_type.model_name</tt>.<br><tt>&nbsp;max((mailbox.resources.disk.allocated or 0) -1, 0)</tt><br><tt>&nbsp;miscellaneous.amount</tt><br><tt>&nbsp;max((account.resources.traffic.used or 0) - getattr(account.miscellaneous.filter(is_active=True, service__name='traffic-prepay').last(), 'amount', 0), 0)</tt>", max_length=256, blank=True)),
                ('nominal_price', models.DecimalField(verbose_name='nominal price', max_digits=12, decimal_places=2)),
                ('tax', models.PositiveIntegerField(verbose_name='tax', choices=[(0, 'Duty free'), (21, '21%')], default=21)),
                ('pricing_period', models.CharField(verbose_name='pricing period', help_text='Time period that is used for computing the rate metric.', blank=True, choices=[('', 'Current value'), ('BILLING_PERIOD', 'Same as billing period'), ('MONTHLY', 'Monthly data'), ('ANUAL', 'Anual data')], max_length=16, default='BILLING_PERIOD')),
                ('rate_algorithm', models.CharField(verbose_name='rate algorithm', help_text='Algorithm used to interprete the rating table.<br>&nbsp;&nbsp;Step price: All price rates with a lower metric are applied.<br>&nbsp;&nbsp;Match price: Only the rate with inmediate inferior metric is applied.', max_length=16, default='STEP_PRICE', choices=[('STEP_PRICE', 'Step price'), ('MATCH_PRICE', 'Match price')])),
                ('on_cancel', models.CharField(verbose_name='on cancel', help_text='Defines the cancellation behaviour of this service.', max_length=16, default='DISCOUNT', choices=[('NOTHING', 'Nothing'), ('DISCOUNT', 'Discount'), ('COMPENSATE', 'Compensat'), ('REFUND', 'Refund')])),
                ('payment_style', models.CharField(verbose_name='payment style', help_text='Designates whether this service should be paid after consumtion (postpay/on demand) or prepaid.', max_length=16, default='PREPAY', choices=[('PREPAY', 'Prepay'), ('POSTPAY', 'Postpay (on demand)')])),
                ('content_type', models.ForeignKey(verbose_name='content type', help_text='Content type of the related service objects.', to='contenttypes.ContentType')),
            ],
        ),
    ]
