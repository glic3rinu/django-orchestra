# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailer', '0003_auto_20150617_1024'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='last_retry',
            new_name='last_try',
        ),
        migrations.AlterField(
            model_name='message',
            name='state',
            field=models.CharField(verbose_name='State', max_length=16, choices=[('QUEUED', 'Queued'), ('SENT', 'Sent'), ('DEFERRED', 'Deferred'), ('FAILED', 'Failed')], default='QUEUED'),
        ),
    ]
