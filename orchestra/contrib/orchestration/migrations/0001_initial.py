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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('backend', models.CharField(verbose_name='backend', max_length=256)),
                ('state', models.CharField(choices=[('RECEIVED', 'RECEIVED'), ('TIMEOUT', 'TIMEOUT'), ('STARTED', 'STARTED'), ('SUCCESS', 'SUCCESS'), ('FAILURE', 'FAILURE'), ('ERROR', 'ERROR'), ('REVOKED', 'REVOKED')], verbose_name='state', max_length=16, default='RECEIVED')),
                ('script', models.TextField(verbose_name='script')),
                ('stdout', models.TextField(verbose_name='stdout')),
                ('stderr', models.TextField(verbose_name='stdin')),
                ('traceback', models.TextField(verbose_name='traceback')),
                ('exit_code', models.IntegerField(null=True, verbose_name='exit code')),
                ('task_id', models.CharField(null=True, verbose_name='task ID', unique=True, max_length=36, help_text='Celery task ID when used as execution backend')),
                ('created_at', models.DateTimeField(verbose_name='created', auto_now_add=True)),
                ('updated_at', models.DateTimeField(verbose_name='updated', auto_now=True)),
            ],
            options={
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='BackendOperation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('backend', models.CharField(verbose_name='backend', max_length=256)),
                ('action', models.CharField(verbose_name='action', max_length=64)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('log', models.ForeignKey(related_name='operations', to='orchestration.BackendLog')),
            ],
            options={
                'verbose_name': 'Operation',
                'verbose_name_plural': 'Operations',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('backend', models.CharField(choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MailmanTrafficBash', '[M] Mailman traffic (Bash)'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic'), ('Apache2Backend', '[S] Apache 2'), ('BSCWBackend', '[S] BSCW SaaS'), ('Bind9MasterDomainBackend', '[S] Bind9 master domain'), ('Bind9SlaveDomainBackend', '[S] Bind9 slave domain'), ('DokuWikiMuBackend', '[S] DokuWiki multisite'), ('DovecotPostfixPasswdVirtualUserBackend', '[S] Dovecot-Postfix virtualuser'), ('DrupalMuBackend', '[S] Drupal multisite'), ('GitLabSaaSBackend', '[S] GitLab SaaS'), ('AutoresponseBackend', '[S] Mail autoresponse'), ('MailmanBackend', '[S] Mailman'), ('MySQLBackend', '[S] MySQL database'), ('MySQLUserBackend', '[S] MySQL user'), ('PHPBackend', '[S] PHP FPM/FCGID'), ('PostfixAddressBackend', '[S] Postfix address'), ('StaticBackend', '[S] Static'), ('SymbolicLinkBackend', '[S] Symbolic link webapp'), ('UNIXUserMaildirBackend', '[S] UNIX maildir user'), ('UNIXUserBackend', '[S] UNIX user'), ('WebalizerAppBackend', '[S] Webalizer App'), ('WebalizerBackend', '[S] Webalizer Content'), ('WordPressBackend', '[S] Wordpress'), ('WordpressMuBackend', '[S] Wordpress multisite'), ('WordpressMuBackend', '[S] Wordpress multisite'), ('PhpListSaaSBackend', '[S] phpList SaaS')], verbose_name='backend', max_length=256)),
                ('match', models.CharField(blank=True, default='True', verbose_name='match', max_length=256, help_text='Python expression used for selecting the targe host, <em>instance</em> referes to the current object.')),
                ('is_active', models.BooleanField(verbose_name='active', default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(verbose_name='name', unique=True, max_length=256)),
                ('address', orchestra.models.fields.NullableCharField(blank=True, unique=True, help_text='IP address or domain name', null=True, verbose_name='address', max_length=256)),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('os', models.CharField(choices=[('LINUX', 'Linux')], verbose_name='operative system', max_length=32, default='LINUX')),
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
            field=models.ForeignKey(to='orchestration.Server', related_name='execution_logs', verbose_name='server'),
        ),
        migrations.AlterUniqueTogether(
            name='route',
            unique_together=set([('backend', 'host')]),
        ),
    ]
