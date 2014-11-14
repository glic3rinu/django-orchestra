# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('systemusers', '0002_systemuser_relative_to_main'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='systemuser',
            name='relative_to_main',
        ),
        migrations.AddField(
            model_name='systemuser',
            name='directory',
            field=models.CharField(default='', max_length=256, verbose_name='directory', blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='systemuser',
            name='home',
            field=models.CharField(help_text='This will be your starting location when you login with this sftp user.', max_length=256, verbose_name='home'),
            preserve_default=True,
        ),
    ]
