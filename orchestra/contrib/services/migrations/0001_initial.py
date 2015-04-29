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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('description', models.CharField(verbose_name='description', max_length=256, unique=True)),
                ('match', models.CharField(blank=True, help_text="Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> that designates wheter a <tt>content_type</tt> object is related to this service or not, always evaluates <tt>True</tt> when left blank. Related instance can be instantiated with <tt>instance</tt> keyword or <tt>content_type.model_name</tt>.</br><tt>&nbsp;databaseuser.type == 'MYSQL'</tt><br><tt>&nbsp;miscellaneous.active and str(miscellaneous.identifier).endswith(('.org', '.net', '.com'))</tt><br><tt>&nbsp;contractedplan.plan.name == 'association_fee''</tt><br><tt>&nbsp;instance.active</tt>", max_length=256, verbose_name='match')),
                ('handler_type', models.CharField(blank=True, help_text='Handler used for processing this Service. A handler enables customized behaviour far beyond what options here allow to.', max_length=256, choices=[('', 'Default')], verbose_name='handler')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('ignore_superusers', models.BooleanField(default=True, help_text='Designates whether superuser, staff and friend orders are marked as ignored by default or not.', verbose_name='ignore superuser, staff and friend')),
                ('billing_period', models.CharField(default='ANUAL', help_text='Renewal period for recurring invoicing.', max_length=16, choices=[('', 'One time service'), ('MONTHLY', 'Monthly billing'), ('ANUAL', 'Anual billing')], blank=True, verbose_name='billing period')),
                ('billing_point', models.CharField(default='ON_FIXED_DATE', help_text='Reference point for calculating the renewal date on recurring invoices', max_length=16, choices=[('ON_REGISTER', 'Registration date'), ('ON_FIXED_DATE', 'Fixed billing date')], verbose_name='billing point')),
                ('is_fee', models.BooleanField(default=False, help_text='Designates whether this service should be billed as  membership fee or not', verbose_name='fee')),
                ('order_description', models.CharField(blank=True, help_text="Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> used for generating the description for the bill lines of this services.<br>Defaults to <tt>'%s: %s' % (ugettext(handler.description), instance)</tt>", max_length=128, verbose_name='Order description')),
                ('ignore_period', models.CharField(default='TEN_DAYS', help_text='Period in which orders will be ignored if cancelled. Useful for designating <i>trial periods</i>', max_length=16, choices=[('', 'Never'), ('ONE_DAY', 'One day'), ('TWO_DAYS', 'Two days'), ('TEN_DAYS', 'Ten days'), ('ONE_MONTH', 'One month')], blank=True, verbose_name='ignore period')),
                ('metric', models.CharField(blank=True, help_text="Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> used for obtinging the <i>metric value</i> for the pricing rate computation. Number of orders is used when left blank. Related instance can be instantiated with <tt>instance</tt> keyword or <tt>content_type.model_name</tt>.<br><tt>&nbsp;max((mailbox.resources.disk.allocated or 0) -1, 0)</tt><br><tt>&nbsp;miscellaneous.amount</tt><br><tt>&nbsp;max((account.resources.traffic.used or 0) - getattr(account.miscellaneous.filter(is_active=True, service__name='traffic-prepay').last(), 'amount', 0), 0)</tt>", max_length=256, verbose_name='metric')),
                ('nominal_price', models.DecimalField(verbose_name='nominal price', decimal_places=2, max_digits=12)),
                ('tax', models.PositiveIntegerField(default=0, verbose_name='tax', choices=[(0, 'Duty free'), (21, '21%')])),
                ('pricing_period', models.CharField(default='BILLING_PERIOD', help_text='Time period that is used for computing the rate metric.', max_length=16, choices=[('', 'Current value'), ('BILLING_PERIOD', 'Same as billing period'), ('MONTHLY', 'Monthly data'), ('ANUAL', 'Anual data')], blank=True, verbose_name='pricing period')),
                ('rate_algorithm', models.CharField(default='MATCH_PRICE', help_text='Algorithm used to interprete the rating table.<br>&nbsp;&nbsp;Match price: Only <b>the rate</b> with a) inmediate inferior metric and b) lower price is applied. Nominal price will be used when initial block is missing.<br>&nbsp;&nbsp;Step price: All rates with a quantity lower than the metric are applied. Nominal price will be used when initial block is missing.', max_length=16, choices=[('MATCH_PRICE', 'Match price'), ('STEP_PRICE', 'Step price')], verbose_name='rate algorithm')),
                ('on_cancel', models.CharField(default='DISCOUNT', help_text='Defines the cancellation behaviour of this service.', max_length=16, choices=[('NOTHING', 'Nothing'), ('DISCOUNT', 'Discount'), ('COMPENSATE', 'Compensat'), ('REFUND', 'Refund')], verbose_name='on cancel')),
                ('payment_style', models.CharField(default='PREPAY', help_text='Designates whether this service should be paid after consumtion (postpay/on demand) or prepaid.', max_length=16, choices=[('PREPAY', 'Prepay'), ('POSTPAY', 'Postpay (on demand)')], verbose_name='payment style')),
                ('content_type', models.ForeignKey(help_text='Content type of the related service objects.', to='contenttypes.ContentType', verbose_name='content type')),
            ],
        ),
    ]
