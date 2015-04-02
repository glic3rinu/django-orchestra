# -*- coding: utf-8 -*-

from django.db import models, migrations
import orchestra.core.validators
import orchestra.apps.resources.validators
import django.utils.timezone
import orchestra.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('djcelery', '__first__'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonitorData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('monitor', models.CharField(max_length=256, verbose_name='monitor', choices=[(b'Apache2Traffic', '[M] Apache 2 Traffic'), (b'MaildirDisk', '[M] Maildir disk usage'), (b'MailmanSubscribers', '[M] Mailman subscribers'), (b'MailmanTraffic', '[M] Mailman traffic'), (b'FTPTraffic', '[M] Main FTP traffic'), (b'SystemUserDisk', '[M] Main user disk'), (b'MysqlDisk', '[M] MySQL disk'), (b'OpenVZTraffic', '[M] OpenVZTraffic')])),
                ('object_id', models.PositiveIntegerField(verbose_name='object id')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created')),
                ('value', models.DecimalField(verbose_name='value', max_digits=16, decimal_places=2)),
                ('content_type', models.ForeignKey(verbose_name='content type', to='contenttypes.ContentType')),
            ],
            options={
                'get_latest_by': 'id',
                'verbose_name_plural': 'monitor data',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Required. 32 characters or fewer. Lowercase letters, digits and hyphen only.', max_length=32, verbose_name='name', validators=[orchestra.core.validators.validate_name])),
                ('verbose_name', models.CharField(max_length=256, verbose_name='verbose name')),
                ('period', models.CharField(default=b'LAST', help_text='Operation used for aggregating this resource monitored data.', max_length=16, verbose_name='period', choices=[(b'LAST', 'Last'), (b'MONTHLY_SUM', 'Monthly Sum'), (b'MONTHLY_AVG', 'Monthly Average')])),
                ('on_demand', models.BooleanField(default=False, help_text='If enabled the resource will not be pre-allocated, but allocated under the application demand', verbose_name='on demand')),
                ('default_allocation', models.PositiveIntegerField(help_text='Default allocation value used when this is not an on demand resource', null=True, verbose_name='default allocation', blank=True)),
                ('unit', models.CharField(help_text='The unit in which this resource is represented. For example GB, KB or subscribers', max_length=16, verbose_name='unit')),
                ('scale', models.CharField(help_text='Scale in which this resource monitoring resoults should be prorcessed to match with unit. e.g. <tt>10**9</tt>', max_length=32, verbose_name='scale', validators=[orchestra.apps.resources.validators.validate_scale])),
                ('disable_trigger', models.BooleanField(default=False, help_text='Disables monitors exeeded and recovery triggers', verbose_name='disable trigger')),
                ('monitors', orchestra.models.fields.MultiSelectField(blank=True, help_text='Monitor backends used for monitoring this resource.', max_length=256, verbose_name='monitors', choices=[(b'Apache2Traffic', '[M] Apache 2 Traffic'), (b'MaildirDisk', '[M] Maildir disk usage'), (b'MailmanSubscribers', '[M] Mailman subscribers'), (b'MailmanTraffic', '[M] Mailman traffic'), (b'FTPTraffic', '[M] Main FTP traffic'), (b'SystemUserDisk', '[M] Main user disk'), (b'MysqlDisk', '[M] MySQL disk'), (b'OpenVZTraffic', '[M] OpenVZTraffic')])),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('content_type', models.ForeignKey(help_text='Model where this resource will be hooked.', to='contenttypes.ContentType')),
                ('crontab', models.ForeignKey(blank=True, to='djcelery.CrontabSchedule', help_text='Crontab for periodic execution. Leave it empty to disable periodic monitoring', null=True, verbose_name='crontab')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(verbose_name='object id')),
                ('used', models.DecimalField(verbose_name='used', null=True, editable=False, max_digits=16, decimal_places=2)),
                ('updated_at', models.DateTimeField(verbose_name='updated', null=True, editable=False)),
                ('allocated', models.DecimalField(null=True, verbose_name='allocated', max_digits=8, decimal_places=2, blank=True)),
                ('content_type', models.ForeignKey(verbose_name='content type', to='contenttypes.ContentType')),
                ('resource', models.ForeignKey(related_name='dataset', verbose_name='resource', to='resources.Resource')),
            ],
            options={
                'verbose_name_plural': 'resource data',
            },
            bases=(models.Model,),
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
