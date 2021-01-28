# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-28 18:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orchestration', '0006_auto_20160219_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='backend',
            field=models.CharField(choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('ApacheTrafficByName', '[M] ApacheTrafficByName'), ('DokuWikiMuTraffic', '[M] DokuWiki MU Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MysqlDisk', '[M] MySQL disk'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('ProxmoxOpenVZTraffic', '[M] ProxmoxOpenVZTraffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic'), ('WordpressMuTraffic', '[M] Wordpress MU Traffic'), ('NextCloudDiskQuota', '[M] nextCloud SaaS Disk Quota'), ('NextcloudTraffic', '[M] nextCloud SaaS Traffic'), ('OwnCloudDiskQuota', '[M] ownCloud SaaS Disk Quota'), ('OwncloudTraffic', '[M] ownCloud SaaS Traffic'), ('PhpListTraffic', '[M] phpList SaaS Traffic'), ('Apache2Controller', '[S] Apache 2'), ('BSCWController', '[S] BSCW SaaS'), ('Bind9MasterDomainController', '[S] Bind9 master domain'), ('Bind9SlaveDomainController', '[S] Bind9 slave domain'), ('DokuWikiMuController', '[S] DokuWiki multisite'), ('DrupalMuController', '[S] Drupal multisite'), ('GitLabSaaSController', '[S] GitLab SaaS'), ('LetsEncryptController', "[S] Let's encrypt!"), ('LxcController', '[S] LxcController'), ('AutoresponseController', '[S] Mail autoresponse'), ('MailScannerSpamRuleController', '[S] MailScanner ruleset'), ('MailmanController', '[S] Mailman'), ('MailmanVirtualDomainController', '[S] Mailman virtdomain-only'), ('MoodleController', '[S] Moodle'), ('MoodleWWWRootController', '[S] Moodle WWWRoot (required)'), ('MoodleMuController', '[S] Moodle multisite'), ('MySQLController', '[S] MySQL database'), ('MySQLUserController', '[S] MySQL user'), ('PHPController', '[S] PHP FPM/FCGID'), ('PangeaProxmoxOVZ', '[S] PangeaProxmoxOVZ'), ('PostfixAddressController', '[S] Postfix address'), ('PostfixAddressVirtualDomainController', '[S] Postfix address virtdomain-only'), ('PostfixRecipientAccessController', '[S] Postfix recipient access'), ('ProxmoxOVZ', '[S] ProxmoxOVZ'), ('uWSGIPythonController', '[S] Python uWSGI'), ('StaticController', '[S] Static'), ('SymbolicLinkController', '[S] Symbolic link webapp'), ('SyncBind9MasterDomainController', '[S] Sync Bind9 master domain'), ('SyncBind9SlaveDomainController', '[S] Sync Bind9 slave domain'), ('UNIXUserMaildirController', '[S] UNIX maildir user'), ('UNIXUserController', '[S] UNIX user'), ('WebalizerAppController', '[S] Webalizer App'), ('WebalizerController', '[S] Webalizer Content'), ('WordPressForceSSLController', '[S] WordPress Force SSL'), ('WordPressURLController', '[S] WordPress URL'), ('WordPressController', '[S] Wordpress'), ('WordpressMuController', '[S] Wordpress multisite'), ('NextCloudController', '[S] nextCloud SaaS'), ('OwnCloudController', '[S] ownCloud SaaS'), ('PhpListSaaSController', '[S] phpList SaaS')], max_length=256, verbose_name='backend'),
        ),
        migrations.AlterField(
            model_name='route',
            name='host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='routes', to='orchestration.Server', verbose_name='host'),
        ),
    ]