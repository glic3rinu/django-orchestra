# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.contrib.resources.validators
import orchestra.models.fields
import django.utils.timezone
import orchestra.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('djcelery', '__first__'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonitorData',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('monitor', models.CharField(choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic')], max_length=256, verbose_name='monitor')),
                ('object_id', models.PositiveIntegerField(verbose_name='object id')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created')),
                ('value', models.DecimalField(decimal_places=2, max_digits=16, verbose_name='value')),
                ('content_type', models.ForeignKey(verbose_name='content type', to='contenttypes.ContentType')),
            ],
            options={
                'get_latest_by': 'id',
                'verbose_name_plural': 'monitor data',
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(validators=[orchestra.core.validators.validate_name], help_text='Required. 32 characters or fewer. Lowercase letters, digits and hyphen only.', max_length=32, verbose_name='name')),
                ('verbose_name', models.CharField(max_length=256, verbose_name='verbose name')),
                ('aggregation', models.CharField(choices=[('last-10-days-avg', 'Last 10 days AVG'), ('last', 'Last value'), ('monthly-avg', 'Monthly AVG'), ('monthly-sum', 'Monthly Sum')], help_text='Method used for aggregating this resource monitored data.', max_length=16, default='last-10-days-avg', verbose_name='aggregation')),
                ('on_demand', models.BooleanField(help_text='If enabled the resource will not be pre-allocated, but allocated under the application demand', default=False, verbose_name='on demand')),
                ('default_allocation', models.PositiveIntegerField(help_text='Default allocation value used when this is not an on demand resource', blank=True, null=True, verbose_name='default allocation')),
                ('unit', models.CharField(help_text='The unit in which this resource is represented. For example GB, KB or subscribers', max_length=16, verbose_name='unit')),
                ('scale', models.CharField(validators=[orchestra.contrib.resources.validators.validate_scale], help_text='Scale in which this resource monitoring resoults should be prorcessed to match with unit. e.g. <tt>10**9</tt>', max_length=32, verbose_name='scale')),
                ('disable_trigger', models.BooleanField(help_text='Disables monitors exeeded and recovery triggers', default=False, verbose_name='disable trigger')),
                ('monitors', orchestra.models.fields.MultiSelectField(choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic')], blank=True, help_text='Monitor backends used for monitoring this resource.', max_length=256, verbose_name='monitors')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('content_type', models.ForeignKey(help_text='Model where this resource will be hooked.', to='contenttypes.ContentType')),
                ('crontab', models.ForeignKey(help_text='Crontab for periodic execution. Leave it empty to disable periodic monitoring', to='djcelery.CrontabSchedule', verbose_name='crontab', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceData',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(verbose_name='object id')),
                ('used', models.DecimalField(decimal_places=3, editable=False, max_digits=16, null=True, verbose_name='used')),
                ('updated_at', models.DateTimeField(editable=False, null=True, verbose_name='updated')),
                ('allocated', models.DecimalField(decimal_places=2, max_digits=8, blank=True, null=True, verbose_name='allocated')),
                ('content_type', models.ForeignKey(verbose_name='content type', to='contenttypes.ContentType')),
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
