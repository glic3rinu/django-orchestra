# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='last_retry',
            field=models.DateTimeField(verbose_name='last try'),
        ),
        migrations.AlterField(
            model_name='message',
            name='subject',
            field=models.TextField(verbose_name='subject'),
        ),
    ]
