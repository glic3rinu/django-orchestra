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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('description', models.CharField(unique=True, max_length=256, verbose_name='description')),
                ('match', models.CharField(max_length=256, blank=True, help_text="Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> that designates wheter a <tt>content_type</tt> object is related to this service or not, always evaluates <tt>True</tt> when left blank. Related instance can be instantiated with <tt>instance</tt> keyword or <tt>content_type.model_name</tt>.</br><tt>&nbsp;databaseuser.type == 'MYSQL'</tt><br><tt>&nbsp;miscellaneous.active and str(miscellaneous.identifier).endswith(('.org', '.net', '.com'))</tt><br><tt>&nbsp;contractedplan.plan.name == 'association_fee''</tt><br><tt>&nbsp;instance.active</tt>", verbose_name='match')),
                ('handler_type', models.CharField(max_length=256, blank=True, help_text='Handler used for processing this Service. A handler enables customized behaviour far beyond what options here allow to.', verbose_name='handler', choices=[('', 'Default')])),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('ignore_superusers', models.BooleanField(help_text='Designates whether superuser, staff and friend orders are marked as ignored by default or not.', default=True, verbose_name='ignore superuser, staff and friend')),
                ('billing_period', models.CharField(max_length=16, verbose_name='billing period', blank=True, help_text='Renewal period for recurring invoicing.', default='ANUAL', choices=[('', 'One time service'), ('MONTHLY', 'Monthly billing'), ('ANUAL', 'Anual billing')])),
                ('billing_point', models.CharField(max_length=16, help_text='Reference point for calculating the renewal date on recurring invoices', verbose_name='billing point', default='ON_FIXED_DATE', choices=[('ON_REGISTER', 'Registration date'), ('ON_FIXED_DATE', 'Fixed billing date')])),
                ('is_fee', models.BooleanField(help_text='Designates whether this service should be billed as  membership fee or not', default=False, verbose_name='fee')),
                ('order_description', models.CharField(max_length=128, blank=True, help_text="Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> used for generating the description for the bill lines of this services.<br>Defaults to <tt>'%s: %s' % (ugettext(handler.description), instance)</tt>", verbose_name='Order description')),
                ('ignore_period', models.CharField(max_length=16, verbose_name='ignore period', blank=True, help_text='Period in which orders will be ignored if cancelled. Useful for designating <i>trial periods</i>', default='TEN_DAYS', choices=[('', 'Never'), ('ONE_DAY', 'One day'), ('TWO_DAYS', 'Two days'), ('TEN_DAYS', 'Ten days'), ('ONE_MONTH', 'One month')])),
                ('metric', models.CharField(max_length=256, blank=True, help_text="Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> used for obtinging the <i>metric value</i> for the pricing rate computation. Number of orders is used when left blank. Related instance can be instantiated with <tt>instance</tt> keyword or <tt>content_type.model_name</tt>.<br><tt>&nbsp;max((mailbox.resources.disk.allocated or 0) -1, 0)</tt><br><tt>&nbsp;miscellaneous.amount</tt><br><tt>&nbsp;max((account.resources.traffic.used or 0) - getattr(account.miscellaneous.filter(is_active=True, service__name='traffic-prepay').last(), 'amount', 0), 0)</tt>", verbose_name='metric')),
                ('nominal_price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='nominal price')),
                ('tax', models.PositiveIntegerField(verbose_name='tax', default=21, choices=[(0, 'Duty free'), (21, '21%')])),
                ('pricing_period', models.CharField(max_length=16, verbose_name='pricing period', blank=True, help_text='Time period that is used for computing the rate metric.', default='BILLING_PERIOD', choices=[('', 'Current value'), ('BILLING_PERIOD', 'Same as billing period'), ('MONTHLY', 'Monthly data'), ('ANUAL', 'Anual data')])),
                ('rate_algorithm', models.CharField(max_length=16, help_text='Algorithm used to interprete the rating table.<br>&nbsp;&nbsp;Step price: All rates with a quantity lower than the metric are applied. Nominal price will be used when initial block is missing.<br>&nbsp;&nbsp;Match price: Only <b>the rate</b> with a) inmediate inferior metric and b) lower price is applied. Nominal price will be used when initial block is missing.', verbose_name='rate algorithm', default='STEP_PRICE', choices=[('STEP_PRICE', 'Step price'), ('MATCH_PRICE', 'Match price')])),
                ('on_cancel', models.CharField(max_length=16, help_text='Defines the cancellation behaviour of this service.', verbose_name='on cancel', default='DISCOUNT', choices=[('NOTHING', 'Nothing'), ('DISCOUNT', 'Discount'), ('COMPENSATE', 'Compensat'), ('REFUND', 'Refund')])),
                ('payment_style', models.CharField(max_length=16, help_text='Designates whether this service should be paid after consumtion (postpay/on demand) or prepaid.', verbose_name='payment style', default='PREPAY', choices=[('PREPAY', 'Prepay'), ('POSTPAY', 'Postpay (on demand)')])),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', help_text='Content type of the related service objects.', verbose_name='content type')),
            ],
        ),
    ]
