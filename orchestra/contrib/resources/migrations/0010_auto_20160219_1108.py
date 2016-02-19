# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import orchestra.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0009_auto_20150804_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitordata',
            name='monitor',
            field=models.CharField(db_index=True, choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('ApacheTrafficByName', '[M] ApacheTrafficByName'), ('DokuWikiMuTraffic', '[M] DokuWiki MU Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic'), ('WordpressMuTraffic', '[M] Wordpress MU Traffic'), ('OwnCloudDiskQuota', '[M] ownCloud SaaS Disk Quota'), ('OwncloudTraffic', '[M] ownCloud SaaS Traffic'), ('PhpListTraffic', '[M] phpList SaaS Traffic')], verbose_name='monitor', max_length=256),
        ),
        migrations.AlterField(
            model_name='monitordata',
            name='object_id',
            field=models.PositiveIntegerField(verbose_name='object id'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='disable_trigger',
            field=models.BooleanField(help_text='Disables monitors exeeded and recovery triggers', verbose_name='disable trigger', default=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='monitors',
            field=orchestra.models.fields.MultiSelectField(help_text='Monitor backends used for monitoring this resource.', blank=True, verbose_name='monitors', max_length=256, choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('ApacheTrafficByName', '[M] ApacheTrafficByName'), ('DokuWikiMuTraffic', '[M] DokuWiki MU Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic'), ('WordpressMuTraffic', '[M] Wordpress MU Traffic'), ('OwnCloudDiskQuota', '[M] ownCloud SaaS Disk Quota'), ('OwncloudTraffic', '[M] ownCloud SaaS Traffic'), ('PhpListTraffic', '[M] phpList SaaS Traffic')]),
        ),
        migrations.AlterField(
            model_name='resourcedata',
            name='object_id',
            field=models.PositiveIntegerField(verbose_name='object id'),
        ),
        migrations.AlterIndexTogether(
            name='monitordata',
            index_together=set([('content_type', 'object_id')]),
        ),
        migrations.AlterIndexTogether(
            name='resourcedata',
            index_together=set([('content_type', 'object_id')]),
        ),
    ]
