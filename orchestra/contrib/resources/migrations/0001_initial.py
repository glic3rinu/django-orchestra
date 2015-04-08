# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.core.validators
import orchestra.contrib.resources.validators
import orchestra.models.fields
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('djcelery', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonitorData',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('monitor', models.CharField(choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MailmanTrafficBash', '[M] Mailman traffic (Bash)'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic')], verbose_name='monitor', max_length=256)),
                ('object_id', models.PositiveIntegerField(verbose_name='object id')),
                ('created_at', models.DateTimeField(verbose_name='created', default=django.utils.timezone.now)),
                ('value', models.DecimalField(verbose_name='value', max_digits=16, decimal_places=2)),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(validators=[orchestra.core.validators.validate_name], verbose_name='name', max_length=32, help_text='Required. 32 characters or fewer. Lowercase letters, digits and hyphen only.')),
                ('verbose_name', models.CharField(verbose_name='verbose name', max_length=256)),
                ('aggregation', models.CharField(choices=[('last-10-days-avg', 'Last 10 days AVG'), ('last', 'Last value'), ('monthly-avg', 'Monthly AVG'), ('monthly-sum', 'Monthly Sum')], verbose_name='aggregation', max_length=16, help_text='Method used for aggregating this resource monitored data.', default='last-10-days-avg')),
                ('on_demand', models.BooleanField(verbose_name='on demand', default=False, help_text='If enabled the resource will not be pre-allocated, but allocated under the application demand')),
                ('default_allocation', models.PositiveIntegerField(verbose_name='default allocation', help_text='Default allocation value used when this is not an on demand resource', null=True, blank=True)),
                ('unit', models.CharField(verbose_name='unit', max_length=16, help_text='The unit in which this resource is represented. For example GB, KB or subscribers')),
                ('scale', models.CharField(validators=[orchestra.contrib.resources.validators.validate_scale], verbose_name='scale', max_length=32, help_text='Scale in which this resource monitoring resoults should be prorcessed to match with unit. e.g. <tt>10**9</tt>')),
                ('disable_trigger', models.BooleanField(verbose_name='disable trigger', default=False, help_text='Disables monitors exeeded and recovery triggers')),
                ('monitors', orchestra.models.fields.MultiSelectField(choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MailmanTrafficBash', '[M] Mailman traffic (Bash)'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic')], verbose_name='monitors', max_length=256, help_text='Monitor backends used for monitoring this resource.', blank=True)),
                ('is_active', models.BooleanField(verbose_name='active', default=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', help_text='Model where this resource will be hooked.')),
                ('crontab', models.ForeignKey(verbose_name='crontab', null=True, to='djcelery.CrontabSchedule', blank=True, help_text='Crontab for periodic execution. Leave it empty to disable periodic monitoring')),
            ],
        ),
        migrations.CreateModel(
            name='ResourceData',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('object_id', models.PositiveIntegerField(verbose_name='object id')),
                ('used', models.DecimalField(editable=False, verbose_name='used', max_digits=16, null=True, decimal_places=3)),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='updated', null=True)),
                ('allocated', models.DecimalField(decimal_places=2, verbose_name='allocated', max_digits=8, null=True, blank=True)),
                ('content_type', models.ForeignKey(verbose_name='content type', to='contenttypes.ContentType')),
                ('resource', models.ForeignKey(verbose_name='resource', related_name='dataset', to='resources.Resource')),
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
            unique_together=set([('verbose_name', 'content_type'), ('name', 'content_type')]),
        ),
    ]
