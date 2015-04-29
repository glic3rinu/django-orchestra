# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackendLog',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('backend', models.CharField(max_length=256, verbose_name='backend')),
                ('state', models.CharField(choices=[('RECEIVED', 'RECEIVED'), ('TIMEOUT', 'TIMEOUT'), ('STARTED', 'STARTED'), ('SUCCESS', 'SUCCESS'), ('FAILURE', 'FAILURE'), ('ERROR', 'ERROR'), ('ABORTED', 'ABORTED'), ('REVOKED', 'REVOKED')], max_length=16, default='RECEIVED', verbose_name='state')),
                ('script', models.TextField(verbose_name='script')),
                ('stdout', models.TextField(verbose_name='stdout')),
                ('stderr', models.TextField(verbose_name='stdin')),
                ('traceback', models.TextField(verbose_name='traceback')),
                ('exit_code', models.IntegerField(null=True, verbose_name='exit code')),
                ('task_id', models.CharField(null=True, max_length=36, help_text='Celery task ID when used as execution backend', unique=True, verbose_name='task ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
            ],
            options={
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='BackendOperation',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('backend', models.CharField(max_length=256, verbose_name='backend')),
                ('action', models.CharField(max_length=64, verbose_name='action')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('log', models.ForeignKey(to='orchestration.BackendLog', related_name='operations')),
            ],
            options={
                'verbose_name_plural': 'Operations',
                'verbose_name': 'Operation',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('backend', models.CharField(choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic'), ('Apache2Backend', '[S] Apache 2'), ('BSCWBackend', '[S] BSCW SaaS'), ('Bind9MasterDomainBackend', '[S] Bind9 master domain'), ('Bind9SlaveDomainBackend', '[S] Bind9 slave domain'), ('DokuWikiMuBackend', '[S] DokuWiki multisite'), ('DovecotPostfixPasswdVirtualUserBackend', '[S] Dovecot-Postfix virtualuser'), ('DrupalMuBackend', '[S] Drupal multisite'), ('GitLabSaaSBackend', '[S] GitLab SaaS'), ('AutoresponseBackend', '[S] Mail autoresponse'), ('MailmanBackend', '[S] Mailman'), ('MySQLBackend', '[S] MySQL database'), ('MySQLUserBackend', '[S] MySQL user'), ('PHPBackend', '[S] PHP FPM/FCGID'), ('PostfixAddressBackend', '[S] Postfix address'), ('uWSGIPythonBackend', '[S] Python uWSGI'), ('StaticBackend', '[S] Static'), ('SymbolicLinkBackend', '[S] Symbolic link webapp'), ('SyncBind9MasterDomainBackend', '[S] Sync Bind9 master domain'), ('SyncBind9SlaveDomainBackend', '[S] Sync Bind9 slave domain'), ('UNIXUserMaildirBackend', '[S] UNIX maildir user'), ('UNIXUserBackend', '[S] UNIX user'), ('WebalizerAppBackend', '[S] Webalizer App'), ('WebalizerBackend', '[S] Webalizer Content'), ('WordPressBackend', '[S] Wordpress'), ('WordpressMuBackend', '[S] Wordpress multisite'), ('PhpListSaaSBackend', '[S] phpList SaaS')], max_length=256, verbose_name='backend')),
                ('match', models.CharField(max_length=256, default='True', blank=True, help_text='Python expression used for selecting the targe host, <em>instance</em> referes to the current object.', verbose_name='match')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True, verbose_name='name')),
                ('address', orchestra.models.fields.NullableCharField(null=True, help_text='IP address or domain name', verbose_name='address', max_length=256, unique=True, blank=True)),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('os', models.CharField(choices=[('LINUX', 'Linux')], max_length=32, default='LINUX', verbose_name='operative system')),
            ],
        ),
        migrations.AddField(
            model_name='route',
            name='host',
            field=models.ForeignKey(to='orchestration.Server', verbose_name='host'),
        ),
        migrations.AddField(
            model_name='backendlog',
            name='server',
            field=models.ForeignKey(verbose_name='server', related_name='execution_logs', to='orchestration.Server'),
        ),
        migrations.AlterUniqueTogether(
            name='route',
            unique_together=set([('backend', 'host')]),
        ),
    ]
