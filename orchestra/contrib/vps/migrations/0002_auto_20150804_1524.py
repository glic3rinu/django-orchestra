# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vps', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vps',
            name='password',
        ),
        migrations.AlterField(
            model_name='vps',
            name='template',
            field=models.CharField(default='debian7', verbose_name='template', choices=[('debian7', 'Debian 7 - Wheezy')], max_length=64, help_text='Initial template.'),
        ),
    ]
