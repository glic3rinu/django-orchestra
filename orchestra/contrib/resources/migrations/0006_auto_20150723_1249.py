# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0005_auto_20150723_0940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitordata',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='created', db_index=True),
        ),
        migrations.AlterField(
            model_name='monitordata',
            name='monitor',
            field=models.CharField(max_length=256, choices=[('Apache2Traffic', '[M] Apache 2 Traffic'), ('DovecotMaildirDisk', '[M] Dovecot Maildir size'), ('Exim4Traffic', '[M] Exim4 traffic'), ('MailmanSubscribers', '[M] Mailman subscribers'), ('MailmanTraffic', '[M] Mailman traffic'), ('MysqlDisk', '[M] MySQL disk'), ('OpenVZTraffic', '[M] OpenVZTraffic'), ('PostfixMailscannerTraffic', '[M] Postfix-Mailscanner traffic'), ('UNIXUserDisk', '[M] UNIX user disk'), ('VsFTPdTraffic', '[M] VsFTPd traffic')], verbose_name='monitor', db_index=True),
        ),
        migrations.AlterField(
            model_name='monitordata',
            name='object_id',
            field=models.PositiveIntegerField(verbose_name='object id', db_index=True),
        ),
    ]
