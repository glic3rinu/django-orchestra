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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('backend', models.CharField(max_length=256, verbose_name='backend')),
                ('state', models.CharField(choices=[('RECEIVED', 'RECEIVED'), ('TIMEOUT', 'TIMEOUT'), ('STARTED', 'STARTED'), ('SUCCESS', 'SUCCESS'), ('FAILURE', 'FAILURE'), ('ERROR', 'ERROR'), ('ABORTED', 'ABORTED'), ('REVOKED', 'REVOKED')], default='RECEIVED', max_length=16, verbose_name='state')),
                ('script', models.TextField(verbose_name='script')),
                ('stdout', models.TextField(verbose_name='stdout')),
                ('stderr', models.TextField(verbose_name='stdin')),
                ('traceback', models.TextField(verbose_name='traceback')),
                ('exit_code', models.IntegerField(verbose_name='exit code', null=True)),
                ('task_id', models.CharField(help_text='Celery task ID when used as execution backend', verbose_name='task ID', unique=True, max_length=36, null=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('backend', models.CharField(max_length=256, verbose_name='backend')),
                ('action', models.CharField(max_length=64, verbose_name='action')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('log', models.ForeignKey(related_name='operations', to='orchestration.BackendLog')),
            ],
            options={
                'verbose_name_plural': 'Operations',
                'verbose_name': 'Operation',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('backend', models.CharField(choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic'), ('Apache2Backend', '[S] Apache 2'), ('BSCWBackend', '[S] BSCW SaaS'), ('Bind9MasterDomainBackend', '[S] Bind9 master domain'), ('Bind9SlaveDomainBackend', '[S] Bind9 slave domain'), ('DokuWikiMuBackend', '[S] DokuWiki multisite'), ('DovecotPostfixPasswdVirtualUserBackend', '[S] Dovecot-Postfix virtualuser'), ('DrupalMuBackend', '[S] Drupal multisite'), ('GitLabSaaSBackend', '[S] GitLab SaaS'), ('AutoresponseBackend', '[S] Mail autoresponse'), ('MailmanBackend', '[S] Mailman'), ('MySQLBackend', '[S] MySQL database'), ('MySQLUserBackend', '[S] MySQL user'), ('PHPBackend', '[S] PHP FPM/FCGID'), ('PostfixAddressBackend', '[S] Postfix address'), ('uWSGIPythonBackend', '[S] Python uWSGI'), ('StaticBackend', '[S] Static'), ('SymbolicLinkBackend', '[S] Symbolic link webapp'), ('UNIXUserMaildirBackend', '[S] UNIX maildir user'), ('UNIXUserBackend', '[S] UNIX user'), ('WebalizerAppBackend', '[S] Webalizer App'), ('WebalizerBackend', '[S] Webalizer Content'), ('WordPressBackend', '[S] Wordpress'), ('WordpressMuBackend', '[S] Wordpress multisite'), ('PhpListSaaSBackend', '[S] phpList SaaS')], max_length=256, verbose_name='backend')),
                ('match', models.CharField(help_text='Python expression used for selecting the targe host, <em>instance</em> referes to the current object.', default='True', blank=True, max_length=256, verbose_name='match')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(unique=True, max_length=256, verbose_name='name')),
                ('address', orchestra.models.fields.NullableCharField(blank=True, max_length=256, null=True, help_text='IP address or domain name', unique=True, verbose_name='address')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('os', models.CharField(choices=[('LINUX', 'Linux')], default='LINUX', max_length=32, verbose_name='operative system')),
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
            field=models.ForeignKey(related_name='execution_logs', to='orchestration.Server', verbose_name='server'),
        ),
        migrations.AlterUniqueTogether(
            name='route',
            unique_together=set([('backend', 'host')]),
        ),
    ]
