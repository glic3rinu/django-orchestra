# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='account',
            name='last_name',
        ),
        migrations.AddField(
            model_name='account',
            name='full_name',
            field=models.CharField(default='', max_length=30, verbose_name='full name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='account',
            name='short_name',
            field=models.CharField(default='', max_length=30, verbose_name='short name', blank=True),
            preserve_default=False,
        ),
    ]
