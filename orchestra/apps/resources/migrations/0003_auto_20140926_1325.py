# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0002_auto_20140926_1143'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monitordata',
            name='date',
        ),
        migrations.RemoveField(
            model_name='resourcedata',
            name='last_update',
        ),
        migrations.AddField(
            model_name='monitordata',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2014, 9, 26, 13, 25, 33, 290000), verbose_name='created', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='resourcedata',
            name='updated_at',
            field=models.DateTimeField(null=True, verbose_name='updated'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='monitordata',
            name='content_type',
            field=models.ForeignKey(verbose_name='content type', to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='monitordata',
            name='object_id',
            field=models.PositiveIntegerField(verbose_name='object id'),
        ),
        migrations.AlterField(
            model_name='resourcedata',
            name='allocated',
            field=models.PositiveIntegerField(null=True, verbose_name='allocated', blank=True),
        ),
        migrations.AlterField(
            model_name='resourcedata',
            name='content_type',
            field=models.ForeignKey(verbose_name='content type', to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='resourcedata',
            name='object_id',
            field=models.PositiveIntegerField(verbose_name='object id'),
        ),
        migrations.AlterField(
            model_name='resourcedata',
            name='resource',
            field=models.ForeignKey(related_name=b'dataset', verbose_name='resource', to='resources.Resource'),
        ),
        migrations.AlterField(
            model_name='resourcedata',
            name='used',
            field=models.PositiveIntegerField(null=True, verbose_name='used'),
        ),
    ]
