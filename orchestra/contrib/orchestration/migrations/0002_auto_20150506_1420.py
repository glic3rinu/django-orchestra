# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orchestration', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='async',
            field=models.BooleanField(help_text='Whether or not block the request/response cycle waitting this backend to finish its execution.', default=False),
        ),
        migrations.AlterField(
            model_name='backendlog',
            name='state',
            field=models.CharField(verbose_name='state', choices=[('RECEIVED', 'RECEIVED'), ('TIMEOUT', 'TIMEOUT'), ('STARTED', 'STARTED'), ('SUCCESS', 'SUCCESS'), ('FAILURE', 'FAILURE'), ('ERROR', 'ERROR'), ('ABORTED', 'ABORTED'), ('REVOKED', 'REVOKED'), ('NOTHING', 'NOTHING')], default='RECEIVED', max_length=16),
        ),
        migrations.AlterField(
            model_name='backendlog',
            name='stderr',
            field=models.TextField(verbose_name='stderr'),
        ),
        migrations.AlterField(
            model_name='route',
            name='backend',
            field=models.CharField(choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic'), ('Apache2Backend', '[S] Apache 2'), ('BSCWBackend', '[S] BSCW SaaS'), ('Bind9MasterDomainBackend', '[S] Bind9 master domain'), ('Bind9SlaveDomainBackend', '[S] Bind9 slave domain'), ('DokuWikiMuBackend', '[S] DokuWiki multisite'), ('DovecotPostfixPasswdVirtualUserBackend', '[S] Dovecot-Postfix virtualuser'), ('DrupalMuBackend', '[S] Drupal multisite'), ('GitLabSaaSBackend', '[S] GitLab SaaS'), ('AutoresponseBackend', '[S] Mail autoresponse'), ('MailmanBackend', '[S] Mailman'), ('MailmanVirtualDomainBackend', '[S] Mailman virtdomain-only'), ('MySQLBackend', '[S] MySQL database'), ('MySQLUserBackend', '[S] MySQL user'), ('PHPBackend', '[S] PHP FPM/FCGID'), ('PostfixAddressBackend', '[S] Postfix address'), ('PostfixAddressVirtualDomainBackend', '[S] Postfix address virtdomain-only'), ('uWSGIPythonBackend', '[S] Python uWSGI'), ('StaticBackend', '[S] Static'), ('SymbolicLinkBackend', '[S] Symbolic link webapp'), ('SyncBind9MasterDomainBackend', '[S] Sync Bind9 master domain'), ('SyncBind9SlaveDomainBackend', '[S] Sync Bind9 slave domain'), ('UNIXUserMaildirBackend', '[S] UNIX maildir user'), ('UNIXUserBackend', '[S] UNIX user'), ('WebalizerAppBackend', '[S] Webalizer App'), ('WebalizerBackend', '[S] Webalizer Content'), ('WordPressBackend', '[S] Wordpress'), ('WordpressMuBackend', '[S] Wordpress multisite'), ('PhpListSaaSBackend', '[S] phpList SaaS')], verbose_name='backend', max_length=256),
        ),
    ]
