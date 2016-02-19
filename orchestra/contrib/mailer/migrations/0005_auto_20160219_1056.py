# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailer', '0004_auto_20150805_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='last_try',
            field=models.DateTimeField(null=True, db_index=True, verbose_name='last try'),
        ),
        migrations.AlterField(
            model_name='message',
            name='priority',
            field=models.PositiveIntegerField(default=2, choices=[(0, 'Critical (not queued)'), (1, 'High'), (2, 'Normal'), (3, 'Low')], db_index=True, verbose_name='Priority'),
        ),
        migrations.AlterField(
            model_name='message',
            name='retries',
            field=models.PositiveIntegerField(default=0, db_index=True, verbose_name='retries'),
        ),
        migrations.AlterField(
            model_name='message',
            name='state',
            field=models.CharField(default='QUEUED', choices=[('QUEUED', 'Queued'), ('SENT', 'Sent'), ('DEFERRED', 'Deferred'), ('FAILED', 'Failed')], db_index=True, max_length=16, verbose_name='State'),
        ),
    ]
