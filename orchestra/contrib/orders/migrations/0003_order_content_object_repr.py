# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20150709_1018'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='content_object_repr',
            field=models.CharField(editable=False, default='', verbose_name='content object repr', max_length=256),
            preserve_default=False,
        ),
    ]
