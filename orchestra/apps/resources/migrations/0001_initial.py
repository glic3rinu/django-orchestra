# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.models.fields
import django.core.validators


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
                ('monitor', models.CharField(max_length=256, verbose_name='monitor', choices=[(b'Apache2Backend', 'Apache 2'), (b'Apache2Traffic', 'Apache 2 Traffic'), (b'AutoresponseBackend', 'Mail autoresponse'), (b'AwstatsBackend', 'Awstats'), (b'Bind9MasterDomainBackend', 'Bind9 master domain'), (b'Bind9SlaveDomainBackend', 'Bind9 slave domain'), (b'DokuWikiMuBackend', 'DokuWiki multisite'), (b'DrupalMuBackend', 'Drupal multisite'), (b'FTPTraffic', 'FTP traffic'), (b'MailSystemUserBackend', 'Mail system user'), (b'MaildirDisk', 'Maildir disk usage'), (b'MailmanBackend', b'Mailman'), (b'MailmanTraffic', b'MailmanTraffic'), (b'MySQLDBBackend', b'MySQL database'), (b'MySQLPermissionBackend', b'MySQL permission'), (b'MySQLUserBackend', b'MySQL user'), (b'MysqlDisk', 'MySQL disk'), (b'OpenVZTraffic', b'OpenVZTraffic'), (b'PHPFPMBackend', 'PHP-FPM'), (b'PHPFcgidBackend', 'PHP-Fcgid'), (b'PostfixAddressBackend', 'Postfix address'), (b'ServiceController', b'ServiceController'), (b'ServiceMonitor', b'ServiceMonitor'), (b'StaticBackend', 'Static'), (b'SystemUserBackend', 'System User'), (b'SystemUserDisk', 'System user disk'), (b'WebalizerBackend', 'Webalizer'), (b'WordpressMuBackend', 'Wordpress multisite')])),
                ('object_id', models.PositiveIntegerField()),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('value', models.DecimalField(verbose_name='value', max_digits=16, decimal_places=2)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
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
                ('name', models.CharField(help_text='Required. 32 characters or fewer. Lowercase letters, digits and hyphen only.', max_length=32, verbose_name='name', validators=[django.core.validators.RegexValidator(b'^[a-z0-9_\\-]+$', 'Enter a valid name.', b'invalid')])),
                ('verbose_name', models.CharField(max_length=256, verbose_name='verbose name')),
                ('period', models.CharField(default=b'LAST', help_text='Operation used for aggregating this resource monitoreddata.', max_length=16, verbose_name='period', choices=[(b'LAST', 'Last'), (b'MONTHLY_SUM', 'Monthly Sum'), (b'MONTHLY_AVG', 'Monthly Average')])),
                ('ondemand', models.BooleanField(default=False, help_text='If enabled the resource will not be pre-allocated, but allocated under the application demand', verbose_name='on demand')),
                ('default_allocation', models.PositiveIntegerField(help_text='Default allocation value used when this is not an on demand resource', null=True, verbose_name='default allocation', blank=True)),
                ('unit', models.CharField(help_text='The unit in which this resource is measured. For example GB, KB or subscribers', max_length=16, verbose_name='unit')),
                ('scale', models.PositiveIntegerField(help_text='Scale in which this resource monitoring resoults should be prorcessed to match with unit.', verbose_name='scale')),
                ('disable_trigger', models.BooleanField(default=False, help_text='Disables monitors exeeded and recovery triggers', verbose_name='disable trigger')),
                ('monitors', orchestra.models.fields.MultiSelectField(blank=True, help_text='Monitor backends used for monitoring this resource.', max_length=256, verbose_name='monitors', choices=[(b'Apache2Backend', 'Apache 2'), (b'Apache2Traffic', 'Apache 2 Traffic'), (b'AutoresponseBackend', 'Mail autoresponse'), (b'AwstatsBackend', 'Awstats'), (b'Bind9MasterDomainBackend', 'Bind9 master domain'), (b'Bind9SlaveDomainBackend', 'Bind9 slave domain'), (b'DokuWikiMuBackend', 'DokuWiki multisite'), (b'DrupalMuBackend', 'Drupal multisite'), (b'FTPTraffic', 'FTP traffic'), (b'MailSystemUserBackend', 'Mail system user'), (b'MaildirDisk', 'Maildir disk usage'), (b'MailmanBackend', b'Mailman'), (b'MailmanTraffic', b'MailmanTraffic'), (b'MySQLDBBackend', b'MySQL database'), (b'MySQLPermissionBackend', b'MySQL permission'), (b'MySQLUserBackend', b'MySQL user'), (b'MysqlDisk', 'MySQL disk'), (b'OpenVZTraffic', b'OpenVZTraffic'), (b'PHPFPMBackend', 'PHP-FPM'), (b'PHPFcgidBackend', 'PHP-Fcgid'), (b'PostfixAddressBackend', 'Postfix address'), (b'ServiceController', b'ServiceController'), (b'ServiceMonitor', b'ServiceMonitor'), (b'StaticBackend', 'Static'), (b'SystemUserBackend', 'System User'), (b'SystemUserDisk', 'System user disk'), (b'WebalizerBackend', 'Webalizer'), (b'WordpressMuBackend', 'Wordpress multisite')])),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
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
                ('object_id', models.PositiveIntegerField()),
                ('used', models.PositiveIntegerField(null=True)),
                ('last_update', models.DateTimeField(null=True)),
                ('allocated', models.PositiveIntegerField(null=True, blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('resource', models.ForeignKey(related_name=b'dataset', to='resources.Resource')),
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
