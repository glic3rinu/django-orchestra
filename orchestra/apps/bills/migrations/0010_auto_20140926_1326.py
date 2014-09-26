# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0009_auto_20140926_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='closed_on',
            field=models.DateField(null=True, verbose_name='closed on', blank=True),
        ),
        migrations.AlterField(
            model_name='bill',
            name='created_on',
            field=models.DateField(auto_now_add=True, verbose_name='created on'),
        ),
        migrations.AlterField(
            model_name='bill',
            name='last_modified_on',
            field=models.DateField(auto_now=True, verbose_name='last modified on'),
        ),
    ]
