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
            field=models.CharField(choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('ApacheTrafficByName', '[M] ApacheTrafficByName'), ('DokuWikiMuTraffic', '[M] DokuWiki MU Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic'), ('WordpressMuTraffic', '[M] Wordpress MU Traffic'), ('OwnCloudDiskQuota', '[M] ownCloud SaaS Disk Quota'), ('OwncloudTraffic', '[M] ownCloud SaaS Traffic'), ('PhpListTraffic', '[M] phpList SaaS Traffic'), ('Apache2Controller', '[S] Apache 2'), ('BSCWController', '[S] BSCW SaaS'), ('Bind9MasterDomainController', '[S] Bind9 master domain'), ('Bind9SlaveDomainController', '[S] Bind9 slave domain'), ('DokuWikiMuController', '[S] DokuWiki multisite'), ('DrupalMuController', '[S] Drupal multisite'), ('GitLabSaaSController', '[S] GitLab SaaS'), ('AutoresponseController', '[S] Mail autoresponse'), ('MailScannerSpamRuleController', '[S] MailScanner ruleset'), ('MailmanController', '[S] Mailman'), ('MailmanVirtualDomainController', '[S] Mailman virtdomain-only'), ('MoodleController', '[S] Moodle'), ('MoodleWWWRootController', '[S] Moodle WWWRoot (required)'), ('MoodleMuController', '[S] Moodle multisite'), ('MySQLController', '[S] MySQL database'), ('MySQLUserController', '[S] MySQL user'), ('PHPController', '[S] PHP FPM/FCGID'), ('PangeaProxmoxOVZ', '[S] PangeaProxmoxOVZ'), ('PostfixAddressController', '[S] Postfix address'), ('PostfixAddressVirtualDomainController', '[S] Postfix address virtdomain-only'), ('PostfixRecipientAccessController', '[S] Postfix recipient access'), ('ProxmoxOVZ', '[S] ProxmoxOVZ'), ('uWSGIPythonController', '[S] Python uWSGI'), ('StaticController', '[S] Static'), ('SymbolicLinkController', '[S] Symbolic link webapp'), ('SyncBind9MasterDomainController', '[S] Sync Bind9 master domain'), ('SyncBind9SlaveDomainController', '[S] Sync Bind9 slave domain'), ('UNIXUserMaildirController', '[S] UNIX maildir user'), ('UNIXUserController', '[S] UNIX user'), ('WebalizerAppController', '[S] Webalizer App'), ('WebalizerController', '[S] Webalizer Content'), ('WordPressURLController', '[S] WordPress URL'), ('WordPressController', '[S] Wordpress'), ('WordpressMuController', '[S] Wordpress multisite'), ('OwnCloudController', '[S] ownCloud SaaS'), ('PhpListSaaSController', '[S] phpList SaaS')], max_length=256, verbose_name='backend'),
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
