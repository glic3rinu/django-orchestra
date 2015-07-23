# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0004_auto_20150503_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitordata',
            name='content_object_repr',
            field=models.CharField(default='', editable=False, max_length=256, verbose_name='content object representation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='resourcedata',
            name='content_object_repr',
            field=models.CharField(default='', editable=False, max_length=256, verbose_name='content object representation'),
            preserve_default=False,
        ),
    ]
