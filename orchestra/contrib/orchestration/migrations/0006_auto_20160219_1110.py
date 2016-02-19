# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import orchestra.core.validators
import orchestra.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('orchestration', '0005_auto_20150709_1016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='backend',
            field=models.CharField(choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('ApacheTrafficByName', '[M] ApacheTrafficByName'), ('DokuWikiMuTraffic', '[M] DokuWiki MU Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic'), ('WordpressMuTraffic', '[M] Wordpress MU Traffic'), ('OwnCloudDiskQuota', '[M] ownCloud SaaS Disk Quota'), ('OwncloudTraffic', '[M] ownCloud SaaS Traffic'), ('PhpListTraffic', '[M] phpList SaaS Traffic'), ('Apache2Backend', '[S] Apache 2'), ('BSCWBackend', '[S] BSCW SaaS'), ('Bind9MasterDomainBackend', '[S] Bind9 master domain'), ('Bind9SlaveDomainBackend', '[S] Bind9 slave domain'), ('DokuWikiMuBackend', '[S] DokuWiki multisite'), ('DrupalMuBackend', '[S] Drupal multisite'), ('GitLabSaaSBackend', '[S] GitLab SaaS'), ('AutoresponseBackend', '[S] Mail autoresponse'), ('MailScannerSpamRuleBackend', '[S] MailScanner ruleset'), ('MailmanBackend', '[S] Mailman'), ('MailmanVirtualDomainBackend', '[S] Mailman virtdomain-only'), ('MoodleBackend', '[S] Moodle'), ('MoodleWWWRootBackend', '[S] Moodle WWWRoot (required)'), ('MoodleMuBackend', '[S] Moodle multisite'), ('MySQLBackend', '[S] MySQL database'), ('MySQLUserBackend', '[S] MySQL user'), ('PHPBackend', '[S] PHP FPM/FCGID'), ('PangeaProxmoxOVZ', '[S] PangeaProxmoxOVZ'), ('PostfixAddressBackend', '[S] Postfix address'), ('PostfixAddressVirtualDomainBackend', '[S] Postfix address virtdomain-only'), ('PostfixRecipientAccessBackend', '[S] Postfix recipient access'), ('ProxmoxOVZ', '[S] ProxmoxOVZ'), ('uWSGIPythonBackend', '[S] Python uWSGI'), ('StaticBackend', '[S] Static'), ('SymbolicLinkBackend', '[S] Symbolic link webapp'), ('SyncBind9MasterDomainBackend', '[S] Sync Bind9 master domain'), ('SyncBind9SlaveDomainBackend', '[S] Sync Bind9 slave domain'), ('UNIXUserMaildirBackend', '[S] UNIX maildir user'), ('UNIXUserBackend', '[S] UNIX user'), ('WebalizerAppBackend', '[S] Webalizer App'), ('WebalizerBackend', '[S] Webalizer Content'), ('WordPressURLBackend', '[S] WordPress URL'), ('WordPressBackend', '[S] Wordpress'), ('WordpressMuBackend', '[S] Wordpress multisite'), ('OwnCloudBackend', '[S] ownCloud SaaS'), ('PhpListSaaSBackend', '[S] phpList SaaS')], max_length=256, verbose_name='backend'),
        ),
        migrations.AlterField(
            model_name='server',
            name='address',
            field=orchestra.models.fields.NullableCharField(help_text='Optional IP address or domain name. If blank, name field will be used for address resolution.<br>If the IP address never changes you can set this field and save DNS requests.', verbose_name='address', validators=[orchestra.core.validators.OrValidator(orchestra.core.validators.validate_ip_address, orchestra.core.validators.validate_hostname)], blank=True, max_length=256, unique=True, null=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='name',
            field=models.CharField(help_text='Verbose name or hostname of this server.', max_length=256, verbose_name='name', unique=True),
        ),
        migrations.AlterIndexTogether(
            name='backendoperation',
            index_together=set([('content_type', 'object_id')]),
        ),
    ]
