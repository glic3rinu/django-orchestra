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
            field=models.CharField(choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic'), ('Apache2Controller', '[S] Apache 2'), ('BSCWController', '[S] BSCW SaaS'), ('Bind9MasterDomainController', '[S] Bind9 master domain'), ('Bind9SlaveDomainController', '[S] Bind9 slave domain'), ('DokuWikiMuController', '[S] DokuWiki multisite'), ('DovecotPostfixPasswdVirtualUserController', '[S] Dovecot-Postfix virtualuser'), ('DrupalMuController', '[S] Drupal multisite'), ('GitLabSaaSController', '[S] GitLab SaaS'), ('AutoresponseController', '[S] Mail autoresponse'), ('MailmanController', '[S] Mailman'), ('MailmanVirtualDomainController', '[S] Mailman virtdomain-only'), ('MySQLController', '[S] MySQL database'), ('MySQLUserController', '[S] MySQL user'), ('PHPController', '[S] PHP FPM/FCGID'), ('PostfixAddressController', '[S] Postfix address'), ('PostfixAddressVirtualDomainController', '[S] Postfix address virtdomain-only'), ('uWSGIPythonController', '[S] Python uWSGI'), ('StaticController', '[S] Static'), ('SymbolicLinkController', '[S] Symbolic link webapp'), ('SyncBind9MasterDomainController', '[S] Sync Bind9 master domain'), ('SyncBind9SlaveDomainController', '[S] Sync Bind9 slave domain'), ('UNIXUserMaildirController', '[S] UNIX maildir user'), ('UNIXUserController', '[S] UNIX user'), ('WebalizerAppController', '[S] Webalizer App'), ('WebalizerController', '[S] Webalizer Content'), ('WordPressController', '[S] Wordpress'), ('WordpressMuController', '[S] Wordpress multisite'), ('PhpListSaaSController', '[S] phpList SaaS')], verbose_name='backend', max_length=256),
        ),
    ]
