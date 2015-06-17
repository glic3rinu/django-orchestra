# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailer', '0002_auto_20150617_1021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='last_retry',
            field=models.DateTimeField(null=True, verbose_name='last try'),
        ),
    ]
