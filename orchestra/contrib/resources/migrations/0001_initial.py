# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import orchestra.contrib.resources.validators
import orchestra.models.fields
import orchestra.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('djcelery', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonitorData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monitor', models.CharField(max_length=256, choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic')], verbose_name='monitor')),
                ('object_id', models.PositiveIntegerField(verbose_name='object id')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created')),
                ('value', models.DecimalField(max_digits=16, decimal_places=2, verbose_name='value')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', verbose_name='content type')),
            ],
            options={
                'verbose_name_plural': 'monitor data',
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(validators=[orchestra.core.validators.validate_name], max_length=32, help_text='Required. 32 characters or fewer. Lowercase letters, digits and hyphen only.', verbose_name='name')),
                ('verbose_name', models.CharField(max_length=256, verbose_name='verbose name')),
                ('aggregation', models.CharField(max_length=16, help_text='Method used for aggregating this resource monitored data.', choices=[('last-10-days-avg', 'Last 10 days AVG'), ('last', 'Last value'), ('monthly-avg', 'Monthly AVG'), ('monthly-sum', 'Monthly Sum')], default='last-10-days-avg', verbose_name='aggregation')),
                ('on_demand', models.BooleanField(help_text='If enabled the resource will not be pre-allocated, but allocated under the application demand', default=False, verbose_name='on demand')),
                ('default_allocation', models.PositiveIntegerField(help_text='Default allocation value used when this is not an on demand resource', blank=True, null=True, verbose_name='default allocation')),
                ('unit', models.CharField(max_length=16, help_text='The unit in which this resource is represented. For example GB, KB or subscribers', verbose_name='unit')),
                ('scale', models.CharField(validators=[orchestra.contrib.resources.validators.validate_scale], max_length=32, help_text='Scale in which this resource monitoring resoults should be prorcessed to match with unit. e.g. <tt>10**9</tt>', verbose_name='scale')),
                ('disable_trigger', models.BooleanField(help_text='Disables monitors exeeded and recovery triggers', default=False, verbose_name='disable trigger')),
                ('monitors', orchestra.models.fields.MultiSelectField(max_length=256, help_text='Monitor backends used for monitoring this resource.', blank=True, choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic')], verbose_name='monitors')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', help_text='Model where this resource will be hooked.')),
                ('crontab', models.ForeignKey(null=True, verbose_name='crontab', to='djcelery.CrontabSchedule', help_text='Crontab for periodic execution. Leave it empty to disable periodic monitoring', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(verbose_name='object id')),
                ('used', models.DecimalField(max_digits=16, editable=False, decimal_places=3, null=True, verbose_name='used')),
                ('updated_at', models.DateTimeField(editable=False, null=True, verbose_name='updated')),
                ('allocated', models.DecimalField(max_digits=8, blank=True, decimal_places=2, null=True, verbose_name='allocated')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', verbose_name='content type')),
                ('resource', models.ForeignKey(related_name='dataset', to='resources.Resource', verbose_name='resource')),
            ],
            options={
                'verbose_name_plural': 'resource data',
            },
        ),
        migrations.AlterUniqueTogether(
            name='resourcedata',
            unique_together=set([('resource', 'content_type', 'object_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='resource',
            unique_together=set([('name', 'content_type'), ('verbose_name', 'content_type')]),
        ),
    ]
